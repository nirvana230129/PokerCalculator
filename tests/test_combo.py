from combo import pack, unpack


def test_pack_round_trip_and_category_dominates_kickers():
    score = pack(6, 12, 11, 0, 0, 0)
    assert unpack(score) == (6, 12, 11, 0, 0, 0)
    assert pack(6, 0) > pack(5, 12, 12, 12, 12, 12)


def test_pack_keeps_four_bits_per_field():
    assert unpack(pack(0x1F, 0x1F)) == (0xF, 0xF, 0, 0, 0, 0)
