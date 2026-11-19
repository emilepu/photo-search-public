import numpy as np

from photosearch.store import duplicate_groups, first_of_each_group


def test_near_copies_share_a_group(store):
    assert store.groups[0] == store.groups[1]
    assert len({int(g) for g in store.groups}) == 4


def test_duplicate_groups_respects_threshold():
    embs = np.array([[1, 0], [0.9, 0.436]], dtype="float32")
    embs /= np.linalg.norm(embs, axis=1, keepdims=True)    # cosine similarity about 0.9
    assert len(set(duplicate_groups(embs, 0.98))) == 2
    assert len(set(duplicate_groups(embs, 0.85))) == 1


def test_duplicate_groups_works_across_blocks():
    embs = np.tile(np.array([[1.0, 0.0]], dtype="float32"), (5, 1))
    assert len(set(duplicate_groups(embs, 0.98, block=2))) == 1


def test_first_of_each_group_keeps_best_ranked():
    assert first_of_each_group([3, 1, 0, 2], np.array([0, 0, 1, 1])) == [3, 1]


def test_full_path_and_copies(store):
    assert store.full_path(0) == "Demo/Birds/owl1.jpg"
    assert store.copies_of(0) == [1]
    assert store.copies_of(3) == []
