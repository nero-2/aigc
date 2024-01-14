class Settings:

    def __init__(self):
        # 平台名称的中英文对照
        self.plat_name = {'汽车行业': 'car_writing', '母婴': 'mother_child', '旅游出行': 'travel',
                     '美食': 'food', '时尚': 'fashion', '家居': 'home', '科技': 'tech',
                     '懂车帝': 'know', '小红书': 'red_book', '头条': 'head', '百家': 'hundred', '汽车之家': 'car_home',
                     '今日头条': 'head', '百家号': 'hundred',
                     '营销节点推广': 'marketing_node', '公司介绍': 'company_intro', '广告slogan': 'advertise_slogan',
                     '品牌介绍': 'brand_intro', 'ip形象介绍': 'ip_image',
                     'AI短视频编剧': 'ai', '视频逐字稿': 'video', '视频营销灵感': 'inspire', '分镜脚本': 'shoot_script',
                     '拍摄剧本': 'shoot', '视频拍摄大纲': 'video_abstract', '企业宣传片脚本': 'publicize',
                     '直播脚本': 'live',
                     '时事政治': 'politics', '商业新闻': 'commercial', '科技新闻': 'technology', '体育新闻': 'PE',
                     '娱乐新闻': 'entertainment', '财经通讯': 'financial'}

        # 文章类型以及平台类型的中英文对照
        self.type_name = {'懂车帝': 'know', '用户口碑': 'user', '对比文案': 'compare', '智慧评论': 'comment',
                     '自定义文案': 'self_def', '爆款标题': 'title',
                     '通稿': 'release', '导购文案': 'guide', '试驾文案': 'drive', '营销软文': 'market',
                     '汽车测评': 'evaluate',
                     '小红书': 'red_book', '今日头条': 'head', '百家号': 'hundred', '汽车之家': 'car_home',
                     '头条': 'head', '百家': 'hundred',
                     }

        # 平台文案对应的文案类型
        self.plat_type = {
            '爆款标题': '爆款标题需要在标题中强调产品所解决的痛点，吸引目标用户点击，你只需要生成文案标题，并且必须控制在20字以内。',
            '种草文案': '种草文案从个人角度向用户推荐产品，需要语言风格口语化，语气亲切，强调个人的使用体验。',
            '测评文案': '测评文案帮助用户了解产品的功能，是用户真实使用产品后对产品属性、效果等进行分析与评价，需要尽量客观准确。',
            '教程文案': '教程文案教读者如何正确或更好的使用产品，需要语言浅显易懂，具有一定的可操作性。',
            '清单文案': '清单文案需要以清单的形式罗列用户所需要的商品或物品，使用户对所需物品更加清晰。',
            '分享爱车': '分享爱车需要介绍车辆的基本信息，突出车辆的优点和美好的个人使用体验。',
            '用车体验': '用车体验需要用户从汽车的个人使用角度，介绍使用汽车带来的感受、生活体验等。',
            '提车作业': '提车作业需要用户分享自己的选车过程，自己的提车价格以及自己提车后的用车感受。',
            '自驾游': '自驾游需要用户分享自己的驾车出游体检，需要包含所驾驶车辆对旅游体验的各种影响。',
            '选买车提问': '选买车提问需要以一问一答的形式，提出与汽车选择、汽车购买等方面相关的重要问题，并利用车辆信息给出解答。',
            '用车问题': '用车问题是用户在汽车使用过程中遇到的不满意的情况，即可以包含已解决的问题，也可以包含未解决的问题。',
            '交流买车': '交流买车是用户在买车前后，针对汽车选择、汽车购买、汽车使用及汽车相关知识等方面进行交流。',
            '用车生活': '用车生活是用户使用汽车的生活体验，主要包括汽车给出行和日常生活带来的各种改变。',
            '改装爱车': '改装爱车是用户对汽车进行改装的分享。一般包括改装目的、改装方案、改装前后的对比和改装的效果等内容。',
            '爱车测评': '爱车测评需要对汽车的各种性能进行测评，一般包括汽车外观、汽车内饰、汽车动力、汽车性能及其他方面，需要采用专业客观的语言风格。',
            '价格讨论': '价格讨论是用户对汽车价格进行比较和讨论。用户需要从汽车质量的角度讨论汽车定价是否合理，性价比如何等话题。',
            '新闻事件型': '新闻事件型文章需要包含时间、地点、人物、时间、原由和事件发生的过程结果，遵循立场中立原则；内容客观真实原则；语言精准、简练、统一的原则，切忌出现口语化。应尽量强调企业文化、优势和亮点，不能直接介绍企业和产品。',
            '争议型': '争议型文章需要在文章中谈论富有争议的内容，以引起更多读者的注意力，使商品具有更高的曝光度。',
            '悬念型': '悬念型文章需要提出问题，围绕问题进行自问自答。问题需要与产品功能相关，但不应该提到产品，回答中可以对产品进行介绍。',
            '诱惑型': '诱惑型文章需要具有较强的实用性，或者访问者可以从中占便宜，让访问者觉得文章对自己有好处。',
            '分享型': '分享型文章需要从用户分享的客观角度宣传商品。使用的语言和语气必须要有生活化的特征，不能过分官方。',
            '情感型': '情感型文章的特点是引起读者情感共鸣。文章不仅要衬托产品，还要让文章富有感染力，让读者在阅读中产生情感共鸣。',
            '故事型': '故事型文章是一种突出故事情节内容的形式，需要兼顾故事的吸引力、品牌的传达、目标读者的需求和文章的整体结构。',
            '促销型': '促销型文章对产品的促销活动进行全面的介绍，包括活动主题、活动内容、活动时间等主要信息。',
            '揭秘型': '揭秘型文章需要带有一定的揭秘性，对产品的行业知识或行业内幕进行揭秘，需要作者对行业内情特别了解。',
            '炒作型': '炒作型文章以第三人称或是第三机构来侧面介绍和推销产品，需要对产品的优点进行重点介绍。',
            '干货型': '干货型文章通常是以专业的角度出发，写作一些对用户有价值的经验案例，可以帮助用户解决生活中的实际问题，需要一定的写作技巧和专业知识，能让用户读之后真的觉得有帮助.',
            '新车测评': '新车评测需要用户对汽车性能进行测试，从舒适、动态、安全、经济、智能等角度对汽车进行评价。需要采用专业客观的语言风格。',
            '行业新闻': '行业新闻是涉及到汽车行业的新闻，需要包含时间、地点、人物、时间、原由和事件发生的过程结果，遵循立场中立原则；内容客观真实原则；语言精准、简练、统一的原则，切忌出现口语化。',
            '产业链分析': '产业链分析首先要确定产业的范畴与产业链的结构，如产业链的上下游及其关系；其次是要确定每个产业环节上有哪些企业，尤其是核心企业、龙头企业；最后需要考虑企业的地域分布以及一些其他角度。',
            '经验分享': '经验分享介绍某件事的经过，以消费者的语气，自然地将经验引入，着重描写自己的感受。',
        }

        # 冬测信息
        self.text_info = '''
        1、引导关注媒体评测方向：采用相同测试标准，领克08冬季续航媒体实测负重纯电续航49.8%，打脸懂车帝，已为领克08正名
        近日，懂车帝混动冬测引发争议，领克08、问界M7等热销车型，不是出现故障提醒，就是表现不佳。对此，许多用户和媒体都表示怀疑。有求真的媒体在懂车帝首轮测试之后也按照同样标准进行了实车实测，数据全程记录。结果显示，领克08在额外负重480斤的情况下纯电续航达成率达到了49.8%。根据用户实际使用的数据显示，领克08非极端环境下，纯电续航达成率可到80%+，就算是在冬季，随着空调和座椅加热的投入使用，纯电续航达成率也能保持在50%左右。
        同样的标准，不一样的结果，懂车帝冬测结果令人捉摸不透，媒体实测全程记录已经有了答案。
        参考话术：
        相同的标准，领克08媒体实测的结果正常且好于懂车帝评测
        媒体实测全程记录，领克08纯电续航达成率成绩打脸懂车帝

        2、怀疑懂车帝公信力方向：信心不足or背后有不能说的秘密？懂车帝冬测门再测再翻车，直播都关了
        懂车帝冬季续航测试遭质疑，问界M7、领克08等热门车型垫底，与很多媒体实际评测的结果相差甚远。近日，懂车帝重测再度翻车，疑似直播也关了！到底是测试本身存在问题，懂车帝方面信心不足，还是背后暗藏玄机，有什么不能对外公开的秘密？懂车帝这项冬季续航评测的公信力正在被击碎，试问这样的评测有什么价值，对于咱们普通消费者来说，会不会存在误导呢？
        参考话术：
        懂车帝冬季续航测试公信力遭质疑，领克08媒体和用户实测结果正常
        与媒体和用户实测成绩差异巨大，懂车帝冬季续航测试公信力堪忧

        3、怀疑懂车帝评测公平性方向：懂车帝变黑车帝？冬季续航评测重启，好巧不巧，质疑懂车帝的问界和领克都双双落后/领克去年一台车才赚40块钱，好不容易出了一个月销破万的08，没钱充值就算了，还要被整。
        知道续航是很多人关注的焦点，懂车帝冬季续航测试博了不少眼球。今年，懂车帝的冬季续航评测问题频出，首测之中，问界M7、领克08这些很多媒体和用户公认不错的车却垫了底。遭到质疑后，近日懂车帝再度开启测试，结果领克08等车型却出现外部温度传感器坏了导致的故障灯提醒，正常测试行驶6.5km后发动机介入就退赛了，导致纯电续航测试草草收场，成为车圈的罗生门。让外界对懂车帝冬测权威性和参考价值产生忧虑，甚至有人怀疑会不会是主办方背后做了小动作，搅浑这潭水。难道懂车帝要变成“黑车帝“了么？
        参考话术：
        懂车帝变身“黑车帝”？领克08懂车帝冬测重启成车圈罗生门
        从测试结果遭质疑到领克08退赛，懂车帝冬季评测为何问题频出？

        4、科普方向：在寒冷的情况下，发动机提前介入属于合理现象。如果是纯电车，这种情况相对就麻烦，但是混动车完全不用担心，依然可以正常使用
        由于此前测试结果中领克08、问界M7等垫底遭到质疑，近日，懂车帝进行冬季续航重测，但是领克08的测试却一波三折，好不容易正常测试行驶6.5km后，因为发动机介入后退赛，导致纯电续航没有完成。此前媒体评测和用户实际使用的数据显示，以懂车帝相同标准测试，零下34度的环境下，额外负重480斤，并全程数据记录，领克08纯电行驶可达92.2公里，纯电续航达成率为49.8%，远高于懂车帝测试。此次重测过程中，发动机提前接入也是正常现象，并不影响实际使用，如果是纯电车可能会有影响，但对于领克08来说，依然可以正常行驶，不怕冷不怕冻，随时满足大家多场景下的出行需求。
        参考话术：
        领克08懂车帝冬季续航重测发动机接入，不影响日常使用
        寒冷天气下领克08发动机接入，媒体和用户实测续航足以满足用户出行
            '''

        # 字数对照
        self.essay_length = {1: '少于400字', 2: '不少于400字,而且不超过800字', 3: '不少于800字'}
        self.essay_length_comment = {1: '15字以内', 2: '15-30字', 3: '30-50字'}
        self.essay_length_redbook = {1: '50-100字', 2: '100-300字', 3: '300-500字'}