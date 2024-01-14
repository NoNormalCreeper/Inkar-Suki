from ... import *


@pytest.mark.skipif('get_tuilan_articles' not in dir(), reason='无api可用')
@pytest.mark.skipif(not Config.jx3api_globaltoken, reason="无apitoken时不测试")
def test_fetch():
    task = Jx3PlayerDetailInfo.from_username('破阵子', '烤冷面不加蛋')
    data = asyncio.run(task)
    assert data.user
    assert data.attribute
    task = Jx3PlayerDetailInfo.from_username('斗转星移', '云澈')
    data = asyncio.run(task)
    assert data.user
    assert data.attribute

    # 判断是否有效存储
    filebase_database.Database.save_all()

@pytest.mark.skipif('get_tuilan_articles' not in dir(), reason='无api可用')
def test_fetch_by_uid():
    task = Jx3PlayerDetailInfo.from_uid('破阵子', '1234')
    data = asyncio.run(task)
    assert data is None  # 不存在或无效的

    task = Jx3PlayerDetailInfo.from_uid('破阵子', '3674275')
    data = asyncio.run(task)
    assert data.user
    assert data.attribute


def test_fetch_and_generate():
    import src.plugins.jx3.user.v3
    func = src.plugins.jx3.user.v3.jx3_attribute3