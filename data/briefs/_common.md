## 通用要求（三人相同，上一轮核查教训已写入）

- 工作目录（一律用绝对路径）：/Users/louwill/Vibing/daily-test/opus5.5-video-test/lives
- 先读 `data/SCHEMA.md`（必须严格遵守）和 `tests/test_data.py`（校验规则）；可参考已完成的 `data/sushi/steps.json`、`data/mao/steps.json` 的写法与粒度。
- 必须用 WebSearch/WebFetch 实际查证，不凭记忆编写。维基百科、百度百科只作辅助（kind 标 secondary/popular）。
- **不得安装任何软件包**（不准 pip/npm/brew install）。只用 Python 标准库、curl、已装的 numpy。农历换算可查公开的历表网页（如中央研究院两千年中西历转换），或在 note 里说明近似。
- 每完成一个人生阶段就把 steps.json / places.json 落盘一次（允许中间状态测试不过）。
- 只修改 `data/<who>/` 和 `data/_build/`（脚本放 `data/_build/<who>_*.py`，缓存放 `data/_build/cache/`）。
- 坐标用 Nominatim 核验（https://nominatim.openstreetmap.org/search?format=json&q=…，带 User-Agent，每秒不超过 1 次，缓存结果；Python 缺证书就用 curl 子进程）。古地名取学界公认今址；查不到取所属县城并标 confidence low，在 note 说明。

上一轮独立核查查出的典型错误，务必避免：
1. **把演义或传说当史实**（例如“挥泪斩谡”出自《三国演义》）。传说只能标 traditional 并写 note；副标题、引文用正史/原文措辞。
2. **跨半年**：农历换算成公历后，事件可能落到另一个半年（例如农历十二月可能已是次年 1 月）。里程碑一律核对换算后的公历月份。
3. **里程碑地点**：milestone.place 必须是事件发生地；该半年的 places 若在事件后还有行程，place 要显式写出，不要默认取半年终点。
4. **引文**必须逐字为原文，篇名正确，并确实出自所标人物或文献；诗文系年有争议的写进 contested。
5. **坐标**：今址偏差要小于 30 km；场所级地点（战场、关隘、寺观）尽量精确。
6. 事件跨半年时的前后两步要互相衔接：上一步的最后一个地点，一般就是下一步的出发地。

完成后运行 `cd /Users/louwill/Vibing/daily-test/opus5.5-video-test/lives && python3 -m pytest -q tests/test_data.py -k <who>`，必须全部通过。
最终回复写明：步数、里程碑列表（id + 标题 + importance + place）、stages（含 mood_hint）、各 confidence 占比，以及没有把握的地方。
