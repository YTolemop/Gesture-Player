import numpy as np
import pytest
from types import SimpleNamespace

from core.channel_model import train, load_model, evaluate, vector
from core.channel_router import OutputRouter
from core.dataset import save_batch, read_batch
from core.types import RawHandSample, Prediction
from network.commands import Commands
from network.pairing import pairing_values
from test_mixed_hands import recipes, hand

CONFIG = {'feature_version': 'mixed-hands-131-v1', 'k': 1, 'distance_threshold': 1., 'vote_threshold': .6}

@pytest.fixture
def reference(monkeypatch):
    _, normalizer, knn = recipes()
    monkeypatch.setattr('core.features.StudentNormalizer', lambda: normalizer)
    monkeypatch.setattr('core.channel_model.StudentKNN', knn)

def sample(left=True, right=True, joint=False):
    return RawHandSample(hand(.2) if left else None, hand(.3 if joint else .8) if right else None, 640, 480, 1.)

def test_three_banks_train_independent_test_and_simultaneous_live_output(reference, tmp_path):
    paths=[]
    for purpose in ('train','test'):
        for channel, raw, label in [('left',sample(True,False),0), ('right',sample(False,True),5), ('both',sample(joint=True),4)]:
            path=tmp_path/f'{purpose}-{channel}.npz'
            save_batch(path,[raw],[label],purpose,CONFIG,channel=channel)
            assert read_batch(path)[2]['channel']==channel
            paths.append(path)
    path=tmp_path/'model.npz'
    report=train(paths,path,CONFIG)
    assert report['channel_samples']=={'left':1,'right':1,'both':1}
    model=load_model(path,CONFIG)
    router=OutputRouter()
    assert router.update(model.predict_channels(sample()))==Commands(left='MOVE_LEFT',right='NORMAL_ATTACK')
    assert router.update(model.predict_channels(sample(False,True)))==Commands(right='NORMAL_ATTACK')
    assert router.update(model.predict_channels(sample(joint=True)))==Commands(both='BLOCK')
    assert router.update(model.predict_channels(sample(False,False)))==Commands()
    result=evaluate(paths,path,CONFIG)
    assert result['independent_test'] and result['samples']==3
    assert all(bank['accuracy']==1 for bank in result['channels'].values())

def test_channel_features_ignore_the_other_hand_and_require_both(reference):
    raw=sample()
    raw.right[0]=np.nan
    assert vector(raw,'left',CONFIG).valid
    assert not vector(raw,'both',CONFIG).valid
    np.testing.assert_array_equal(vector(sample(True,False),'left',CONFIG).features,
                                  vector(sample(),'left',CONFIG).features)
    assert not vector(sample(True,False),'both',CONFIG).valid

def test_joint_filter_warmup_never_leaks_single_actions(monkeypatch):
    class Filter:
        def reset(self):pass
        def update(self,prediction,timestamp):return 'NONE'
    monkeypatch.setattr('core.channel_router.StudentFilter',Filter)
    router=OutputRouter()
    assert router.update({'left':Prediction('JUMP',True,0,1),'right':Prediction('NORMAL_ATTACK',True,0,1),
                          'both':Prediction('BLOCK',True,0,1)},enabled=True)==Commands()
    router.generated-=1
    assert router.read_commands()==Commands()

def test_legacy_batches_are_not_silently_mislabelled(reference,tmp_path):
    path=tmp_path/'old.npz'
    save_batch(path,[sample()],[0],'train',CONFIG)
    before=path.read_bytes()
    with pytest.raises(ValueError,match='未標通道'):
        train([path],tmp_path/'model.npz',CONFIG)
    assert path.read_bytes()==before

def test_numeric_pairing_preserves_leading_zero_and_pve_needs_no_room():
    assert pairing_values('https://ga-game.codpy.org/','','000012')==('https://ga-game.codpy.org','','000012')
    assert pairing_values('https://ga-game.codpy.org','123456','012345')[1]=='123456'
    for room,code in [('ABC123','012345'),('12345','012345'),('123456','12345'),('','１２３４５６')]:
        with pytest.raises(ValueError):pairing_values('https://ga-game.codpy.org',room,code)

def test_weak_or_ambiguous_hand_does_not_clear_the_other(monkeypatch):
    from core.landmarks import Landmarks
    points=[SimpleNamespace(x=float(x),y=float(y),z=float(z)) for x,y,z in hand()]
    detector=Landmarks.__new__(Landmarks)
    detector.last_ms=-1;detector.swap_handedness=False
    for names,scores in [(['Left','Right'],[.1,.99]),(['Left','Left','Right'],[.99,.99,.99])]:
        result=SimpleNamespace(hand_landmarks=[points]*len(names),handedness=[
            [SimpleNamespace(category_name=name,score=score)] for name,score in zip(names,scores)])
        detector.detector=SimpleNamespace(detect_for_video=lambda *_:result)
        raw=detector.detect(np.zeros((480,640,3),np.uint8),1.,{})
        assert raw.left is None and raw.right is not None
