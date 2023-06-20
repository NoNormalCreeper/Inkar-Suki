from src.tools.dep.bot import *
from .api import *
from .renderer import *

jx3_cmd_flower = on_command("jx3_flower", aliases={"花价"}, priority=5)


@jx3_cmd_flower.handle()
async def jx3_flower(state: T_State, event: GroupMessageEvent, args: Message = CommandArg()):
    '''
    获取当前花价
    花价 [区服]
    Example：-交易行 幽月轮 帝骖龙翔 1
    Example：-交易行 帝骖龙翔 2
    '''
    template = [Jx3Arg(Jx3ArgsType.server)]
    arg = get_args(args, template)
    arg_server = arg[0]
    data = await get_flower(arg_server)
    if isinstance(data, str):
        return await jx3_cmd_flower.finish(data)
    img = await renderer(arg_server, data)
    return await jx3_cmd_flower.send(ms.image(Path(img).as_uri()))