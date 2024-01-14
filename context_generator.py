import random
from extract_knowledge import extract_from_db
import os
import json
from buaa_log import Logger
from settings import Settings

log = Logger('logs/context_generator.log', level='debug')


class ContentGenerator:
    """
    生成给chatgpt输入的文案
    """

    def __init__(self, task):
        log.logger.info('对task_id = {} 进行ContentGenerator类初始化'.format(task['task_id']))
        self.settings = Settings()
        self.plat_name = self.settings.plat_name
        self.type_name = self.settings.type_name
        self.plat_type = self.settings.plat_type
        self.text_info = self.settings.text_info
        self.essay_length = self.settings.essay_length
        self.essay_length_comment = self.settings.essay_length_comment
        self.essay_length_redbook = self.settings.essay_length_redbook
        self.platform_name = self.plat_name[task.get('platform_name')]
        self.task_data = task.get('task_data')
        self.input_language = self.task_data.get('input_language')
        self.copy_length = self._copy_length()

    def _copy_length(self):
        copy_length = self.essay_length[int(self.task_data.get('copy_length'))]
        if self.task_data.get('writing_type') == '智慧评论':
            copy_length = self.essay_length_comment[int(self.task_data.get('copy_length'))]
        elif (self.platform_name == 'red_book') or (self.task_data.get('platform_style') == '小红书'):
            copy_length = self.essay_length_redbook[int(self.task_data.get('copy_length'))]
        return copy_length

    # 从SampleLibrary样例类中抽取需要的样例
    @staticmethod
    def sample(type_name):
        url = os.path.join('samplelibrary', type_name)
        population = os.listdir(url)
        samples = random.choice(population)
        with open(os.path.join(url, samples), "r", encoding='utf-8') as f:
            data = f.read()
        return data

    # 根据平台名称的英文名调用相应的方法
    # 比如实现汽车写作，那么该方法会调用car_writing_generator()方法
    def generate(self):
        log.logger.info('调用相应的文案生成函数')
        result = getattr(self, self.platform_name + '_generator')()
        return result

    # ###################### #
    # 实现行业文案的生成         #
    # ###################### #
    # 实现汽车行业的文案生成
    def car_writing_generator(self):
        writing_type = self.task_data.get('writing_type')
        # 汽车写作根据写作类型不同，需要调用不同的方法
        if writing_type == '对比文案':
            res = self._compare()
        elif writing_type == '智慧评论':
            res = self._comment()
        else:
            res = self._default()

        return res

    def _compare(self):
        # 从任务数据中获取需要的信息
        platform_style = self.task_data.get('platform_style')
        writing_type = self.task_data.get('writing_type')
        model = self.task_data.get('model')
        brand = self.task_data.get('brand')
        if brand and model:
            car = brand + ' ' + model
        hotspot_direction = self.task_data.get('hotspot_direction')
        copy_emotion = self.task_data.get('copy_emotion')
        wording_style = self.task_data.get('wording_style')
        self_positioning = self.task_data.get('self_positioning')
        content_theme = self.task_data.get('content_theme')
        keywords = self.task_data.get('keywords')
        # 从数据库获取车的信息
        try:
            msg = extract_from_db(car)
        except:
            msg = None
        # 获得相应的平台样例文章
        plat_sample = self.sample(self.type_name[platform_style])
        # 获得相应的写作类型的样例文章
        writing_sample = self.sample(self.type_name[writing_type])
        compares = json.loads(self.task_data.get('comparison_models'))
        compare_num = len(compares)
        # 获取所有对比车和原车的信息
        cars = [model['brand'] + ' ' + model['model'] for model in compares if model]
        for c in cars:
            try:
                new_msg = extract_from_db((c))
            except:
                new_msg = None
            if msg and new_msg:
                msg += ('\n' + new_msg)
            elif new_msg:
                msg = new_msg
        if msg:
            msg += '\n'
        if brand in model:
            car = model
        result = '''假设你是一名专门为{}用户写文案的专家，你将根据我提供的信息来生成一段符合该平台风格的{}类型的文案，来发表你对车的一些评价与建议。
                        注意使用你总结的{}类型的文案的特点以及{}的平台风格。
                        根据内容主题{}来确定生成文本的主题，文案需要围绕该主题展开，将主题作为主要讨论内容的场景;
                        {}平台当前的热点方向是"{}"，你应当思考一下如何将该热点方向与需要生成的文案形成关联，如果你认为将该热点方向融入到文案中不会使得文案变得不流畅，那么你需要将该热点方向融入到文案之中，否则就无视掉该热点方向。
                        根据文案情感:{}来确定文章的情感调性;根据措辞风格:{}来确定文章的措辞风格;根据关键词:{}来确定文章需要突出的词;
                        根据自我定位:{}来确定品牌或产品的市场定位和目标客户群。若果信息为None，则代表可以无视该信息。
                        要利用{}种车的基本信息来对比介绍，并重点突出{}的优势，车的基本信息为:\n{}。
                        注意:文章要使用{}，对于车的基本信息，应当合理自然的运用到文章之中，而不是简单罗列出来，与此同时你需要严格按照我提供的汽车信息完成创作，严禁使用我未提供的汽车的信息。
                        文章的字数要求为:{}。
                        '''.format(platform_style, writing_type, writing_type, platform_style,
                                   content_theme, platform_style,
                                   hotspot_direction, copy_emotion, wording_style, keywords,
                                   self_positioning, str(compare_num + 1), car, msg, self.input_language,
                                   self.copy_length)
        if platform_style == '小红书':
            result += '要有符合小红书风格的emoji，同时根据文案的关键内容生成tag标签。'
        if writing_type == '用户口碑':
            result += '要以用户的口吻叙述，语言要口语化，富有生活气息。'
        return [plat_sample, writing_sample, result]

    def _comment(self):
        # 从任务数据中获取需要的信息
        platform_style = self.task_data.get('platform_style')
        writing_type = self.task_data.get('writing_type')
        model = self.task_data.get('model')
        brand = self.task_data.get('brand')
        if brand and model:
            car = brand + ' ' + model
        copy_emotion = self.task_data.get('copy_emotion')
        keywords = self.task_data.get('keywords')
        # 获得相应的平台样例文章
        plat_sample = self.sample(self.type_name[platform_style])
        # 获得相应的写作类型的样例文章
        writing_sample = self.sample(self.type_name[writing_type])
        text = self.task_data.get('image_text_link')
        result = '''假设你是一名智慧评论员，你需要使用你总结的智慧评论的风格，以及{}的平台风格，对我提供的信息来生成一条{}平台的智慧评论。
                                你要进行评论的信息为：{}
                                你的评论情感需要是{}，而且你的评论要重点体现{}。
                                注意：你只需要生成一条评论，该评论要使用{}，该评论的字数要求为:{}。
                                '''.format(platform_style, platform_style, text, copy_emotion, keywords,
                                           self.input_language,
                                           self.copy_length)
        if platform_style == '小红书':
            result += '要有符合小红书风格的emoji，同时根据文案的关键内容生成tag标签。'
        if writing_type == '用户口碑':
            result += '要以用户的口吻叙述，语言要口语化，富有生活气息。'

        return [plat_sample, writing_sample, result]

    def _default(self):
        # 从任务数据中获取需要的信息
        platform_style = self.task_data.get('platform_style')
        writing_type = self.task_data.get('writing_type')
        model = self.task_data.get('model')
        brand = self.task_data.get('brand')
        if brand and model:
            car = brand + ' ' + model
        hotspot_direction = self.task_data.get('hotspot_direction')
        copy_emotion = self.task_data.get('copy_emotion')
        wording_style = self.task_data.get('wording_style')
        self_positioning = self.task_data.get('self_positioning')
        content_theme = self.task_data.get('content_theme')
        keywords = self.task_data.get('keywords')
        # 获得相应的平台样例文章
        plat_sample = self.sample(self.type_name[platform_style])
        # 获得相应的写作类型的样例文章
        writing_sample = self.sample(self.type_name[writing_type])
        # 从数据库获取车的信息
        if brand and model:  # 输入车型信息不为空，为具体车辆文案
            car = brand + ' ' + model
            try:
                msg = extract_from_db(car)
            except:
                msg = None
            if brand in model:
                car_name = model
            result = '''假设你是一名专门为{}用户写文案的专家，你将根据我提供的信息来生成一段符合该平台风格的{}类型的文案，来发表你对{}的一些评价与建议，
                    注意使用你总结的{}类型文章的特点以及{}的平台风格。
                    {}平台当前的热点方向是"{}"，你应当思考一下如何将该热点方向与需要生成的文案形成关联，如果你认为将该热点方向融入到文案中不会使得文案变得不流畅，那么你需要将该热点方向融入到文案之中，否则就无视掉该热点方向。
                    根据文案情感:{}来确定文章的情感调性;根据措辞风格:{}来确定文章的措辞风格;根据关键词:{}来确定文章需要突出的词;
                    根据内容主题{}来确定生成文本的主题或焦点，文案需要围绕该主题展开，你需要在文案里体现出该主题，将其作为文案的场景;
                    根据自我定位:{}来确定品牌或产品的市场定位和目标客户群。若果信息为None，则代表可以无视该信息。
                    要利用{}的基本信息来介绍, 车的基本信息为{}。
                    注意:文章要使用{}，对于车的基本信息，应当合理自然的运用到文章之中，而不是简单罗列出来，与此同时你需要严格按照我提供的汽车信息完成创作，严禁使用我未提供的汽车的信息。
                    文章的字数要求为:{}。
                    '''.format(platform_style, writing_type, car_name,
                               writing_type, platform_style, platform_style, hotspot_direction,
                               copy_emotion, wording_style, keywords, content_theme, self_positioning, car, msg,
                               self.input_language, self.copy_length)
        else:  # 车型信息为空，为品牌文案生成
            try:
                msg = extract_from_db(brand)
            except:
                msg = None
            result = '''假设你是一名专门为{}用户写文案的专家，你将根据我提供的信息来生成一段符合该平台风格的{}类型的文案，
                    请你帮我基于汽车品牌{},基于以下事件作为主要内容{};生成该企业的品牌总结性的年度盘点文案，不需要写出具体日期，只需生成大段的总结性文案即可，
                    不要生成“近期”“近日”此种语句。文案语言风格仿照以下样例“日前，乘联会发布了2023年12月份零售销量快报，快报显示2023年全年中国乘用车累计销量2170.3万辆，同比增长5.6%，其中新能源车全年累计销量为774万辆，同比增长了36.3%。在新能源车零售销量TOP的榜单中，理想汽车增速接近翻倍，但比亚迪、特斯拉、埃安把持前三名的格局仍然没有改变。广汽埃安全年销量483632辆，同比增长76.7%，排名第三。广汽埃安自2022年突然发力，一路冲到了新能源车销量的前三甲位置，其中AION S和AION Y两款车型功不可没，2023年，AION S的销量为220904辆，AION Y的销量为235717辆。去年下半年以来，广汽埃安重点进行了对昊铂品牌的布局，先后推出了昊铂GT、昊铂SSR以及昊铂HT等车型，为2024年的持续增长奠定了基础。吉利汽车全年销量469427辆，同比增长54%，排名第四。吉利是自主品牌阵营中新能源车销量增长较快的车企，虽然看单车销量并没有特别火热的爆款，但是吉利旗下各个品牌发展都比较均衡，吉利银河、吉利几何、极氪等品牌在2023年的新能源销量中都屡创新高。”
                    注意使用你总结的{}类型文章的特点以及{}的平台风格。
                    {}平台当前的热点方向是"{}"，你应当思考一下如何将该热点方向与需要生成的文案形成关联，如果你认为将该热点方向融入到文案中不会使得文案变得不流畅，那么你需要将该热点方向融入到文案之中，否则就无视掉该热点方向。
                    根据文案情感:{}来确定文章的情感调性;根据措辞风格:{}来确定文章的措辞风格;根据关键词:{}来确定文章需要突出的词;
                    根据内容主题{}来确定生成文本的主题或焦点，文案需要围绕该主题展开，你需要在文案里体现出该主题，将其作为文案的场景;
                    根据自我定位:{}来确定品牌或产品的市场定位和目标客户群。若果信息为None，则代表可以无视该信息。
                    注意:文章要使用{},文章的字数要求为:{}。
                    '''.format(platform_style, writing_type, brand, msg,
                               writing_type, platform_style, platform_style, hotspot_direction,
                               copy_emotion, wording_style, keywords, content_theme, self_positioning,
                               self.input_language, self.copy_length)
        if platform_style == '小红书':
            result += '要有符合小红书风格的emoji，同时根据文案的关键内容生成tag标签。'
        if writing_type == '用户口碑':
            result += '要以用户的口吻叙述，语言要口语化，富有生活气息。'
        if content_theme is not None:
            if '冬测' in content_theme or '冬季测试' in content_theme:
                text_info = '懂车帝冬测相关信息如下,学习下列的关键话术,在后续的文案生成中体现出懂车帝对领克08的冬测失误,从而凸显领克08的优越性能\n'
                text_info += '冬测信息：' + self.text_info
                result += '要在文案中说明懂车帝测试的不公平，利用前述的参考话术进行相应的回应。'
                return [plat_sample, writing_sample, text_info, result]
        return [plat_sample, writing_sample, result]

    # 实现母婴的行业文案生成
    def mother_child_generator(self):
        # 加载信息
        marketing_theme = self.task_data.get('marketing_theme')
        product_type = self.task_data.get('product_type')
        target_group = self.task_data.get('target_group')
        core_selling_point = self.task_data.get('core_selling_point')
        prompt = """我是一名营销策划者，假设你是一名母婴用品行业的营销文案策划师，
                现在需要你基于的{}营销主体，其商品类型为{}，针对{}这一目标人群，围绕核心卖点{}，生成一条{}的{}营销文案。
                生成文案可以考虑多感官的使用，同时生成的文案请保持客观性，不要在我未提及的情况下额外添加符合某些国家、行业标准要求的信息
                """.format(marketing_theme, product_type, target_group, core_selling_point, self.copy_length,
                           self.input_language)
        return prompt

    # 实现旅游出行的行业文案生成
    def travel_generator(self):
        region_choice = self.task_data.get('region_choice')
        theme_description = self.task_data.get('theme_description')
        scene_theme = self.task_data.get('scene_theme')
        key_information = self.task_data.get('key_information')
        if scene_theme == "旅游攻略":
            prompt = """你是一名有着丰富旅行经验的旅行家，
                现在需要你基于{}地区，围绕{}的主题内容描述，
                在{}这一创造要求下，围绕关键信息{}，
                生成{}的{}旅行攻略。
                请避免使用空泛夸赞文案，类似于“优秀的质量”，同时生成的文案请保持客观性，同时需要注意旅游攻略文案的如下要点：开头：黄金三秒，一定要能吸引住用户继续看下去，可以多看同类型爆款开头文案，积累收藏，借鉴格式引导：将发人深思、让人好奇、刺激的内容放到前面，作为内容的引子内容：旅行攻略一般按照时间或景点的顺序，进行经验/千货分享，结构为：景点＋体验＋感受风格：短视频文案区别于书面语言，一定要口语化、接地气，不需要大篇幅去形容美景，多注重推荐景点和体验方式、体验感受。可以根据自己面向的用户，调整攻略的体验重点亮点：文案要区别于千篇一律的攻略，可以表达自己的观点和推荐，会让你的内容更有辨识度结尾：引导点赞和收藏，用能够带给观众价值的内容，或情绪话术，吸引观众前来游玩
                """.format(region_choice, theme_description, scene_theme, key_information, self.copy_length,
                           self.input_language)
        else:
            prompt = """我是一名营销文案的策划者，假设你是一名旅游出行行业的营销文案策划师，
                现在需要你基于{}地区，围绕{}的主题内容描述，
                在{}这一场景下，围绕关键信息{}，
                生成{}的{}营销文案。
                避免使用空泛夸赞文案，类似于“优秀的质量”，同时生成的文案请保持客观性，不要在我未提及的情况下额外添加符合某些国家标准要求的信息
                """.format(region_choice, theme_description, scene_theme, key_information, self.copy_length,
                           self.input_language)

        return prompt

    # 实现美食的行业文案生成
    def food_generator(self):
        copywriting_direction = self.task_data.get('copywriting_direction')
        if copywriting_direction == "探店":
            copywriting_direction = self.task_data.get('copywriting_direction')
            store = self.task_data.get('store')
            food_product = self.task_data.get('food_product')
            product_introduction = self.task_data.get('product_introduction')
            keywords = self.task_data.get('keywords')
            prompt = """我是一名美食探店的博主，现在假设你是一名美食行业的探店博主需要完成第一人称的用餐体验，
                现在需要你基于{}文案的方向，围绕商家{}的产品{},
                基于如下产品介绍{}，围绕关键词{}，
                生成{}的{}探店文案。
                生成文案可以考虑菜品本身之外多感官多角度体验的使用，例如“店铺的环境、地理位置、服务人员服务态度、等待时间、菜品质量等等”，避免使用空泛夸赞文案，类似于“优秀的质量”
                注意使用你总结的探店文案的风格。
                """.format(copywriting_direction, store, food_product, product_introduction, keywords,
                           self.copy_length, self.input_language)
            scout_sample = self.sample("scout")
            return [scout_sample, prompt]
        else:
            copywriting_direction = self.task_data.get('copywriting_direction')
            marketing_theme = self.task_data.get('marketing_theme')
            ingredient_attributes = self.task_data.get('ingredient_attributes')
            core_selling_point = self.task_data.get('core_selling_point')
            prompt = """我是一名营销文案的策划者，现在假设你是一名美食行业的营销文案策划师，
                现在需要你基于{}的文案方向，围绕{}的营销主题，
                针对{}的食材属性，围绕核心卖点{}，
                生成{}的{}营销文案。
                生成文案可以考虑多感官体验的使用，避免使用空泛夸赞文案，类似于“优秀的质量”，同时生成的文案请保持客观性，不要在我未提及的情况下额外添加符合某些国家标准要求的信息
                """.format(copywriting_direction, marketing_theme, ingredient_attributes, core_selling_point,
                           self.copy_length, self.input_language)

        return prompt

    # 实现时尚的行业文案生成
    def fashion_generator(self):
        type_selection = self.task_data.get('type_selection')
        if type_selection == "穿搭":
            type_selection = self.task_data.get('type_selection')
            marketing_theme = self.task_data.get('marketing_theme')
            content_scene = self.task_data.get('content_scene')
            season = self.task_data.get('season')
            prompt = """我是一名营销文案的策划者，现在假设你是一名时尚行业的营销文案策划师，
                    现在需要你基于{}这一时尚类型，围绕{}的营销主题
                    针对{}的内容场景，围绕{}这一季节，
                    生成{}的{}营销文案。
                    避免使用空泛夸赞文案，类似于“优秀的质量”，同时生成的文案请保持客观性，不要在我未提及的情况下额外添加符合某些国家标准要求的信息
                    """.format(type_selection, marketing_theme, content_scene, season, self.copy_length,
                               self.input_language)
        else:
            type_selection = self.task_data.get('type_selection')
            product_type = self.task_data.get('product_type')
            brand_query = self.task_data.get('brand_query')
            keywords = self.task_data.get('keywords')
            prompt = """我是一名营销文案的策划者，现在假设你是一名时尚行业的营销文案策划师，
                    现在需要你基于{}这一时尚类型，围绕{}品牌的{}这一产品，
                    基于以下关键词{},
                    生成{}的{}营销文案。
                    避免使用空泛夸赞文案，类似于“优秀的质量”，同时生成的文案请保持客观性，不要在我未提及的情况下额外添加符合某些国家标准要求的信息
                    """.format(type_selection, brand_query, product_type, keywords, self.copy_length,
                               self.input_language)

        return prompt

    # 实现家居的行业文案生成
    def home_generator(self):
        content_direction = self.task_data.get('content_direction')
        if content_direction == "家居家装":
            marketing_theme = self.task_data.get('marketing_theme')
            copy_type = self.task_data.get('copy_type')
            product_type = self.task_data.get('product_type')
            content_description = self.task_data.get('content_description')
            prompt = """我是一名营销文案的策划者，现在假设你是一名家居行业的营销文案策划师，
                    现在需要你基于{}这一内容方向，围绕{}这一营销主体，
                    基于{}的文案类型，{}的产品类型，围绕{}的内容描述
                    生成{}的{}营销文案。
                    生成文案可以考虑多感官体验的使用，避免使用空泛夸赞文案，类似于“优秀的质量”，同时生成的文案请保持客观性，不要在我未提及的情况下额外添加符合某些国家标准要求的信息
                    """.format(content_direction, marketing_theme, copy_type, product_type, content_description,
                               self.copy_length, self.input_language)
        elif content_direction == "居家用品":
            marketing_theme = self.task_data.get('marketing_theme')
            product_type = self.task_data.get('product_type')
            core_selling_points = self.task_data.get('core_selling_points')
            prompt = """我是一名营销文案的策划者，现在假设你是一名家居行业的营销文案策划师，
                    现在需要你基于{}这一内容方向，围绕{}这一营销主体，
                    基于{}的产品类型，围绕{}的核心卖点
                    生成{}的{}营销文案。
                    生成文案可以考虑多感官体验的使用，避免使用空泛夸赞文案，类似于“优秀的质量”，同时生成的文案请保持客观性，不要在我未提及的情况下额外添加符合某些国家标准要求的信息
                    """.format(content_direction, marketing_theme, product_type, core_selling_points,
                               self.copy_length, self.input_language)
        elif content_direction == "家电行情":
            marketing_theme = self.task_data.get('marketing_theme')
            appliance_type = self.task_data.get('appliance_type')
            content_description = self.task_data.get('content_description')
            content_style = self.task_data.get('content_style')
            prompt = """我是一名营销文案的策划者，现在假设你是一名家居行业的营销文案策划师，
                    现在需要你基于{}这一内容方向，围绕{}这一营销主体，
                    基于{}的家电类型，围绕{}的内容描述，基于{}的文案风格要求，
                    生成{}的{}营销文案。
                    生成文案可以考虑多感官体验的使用，避免使用空泛夸赞文案，类似于“优秀的质量”，同时生成的文案请保持客观性，不要在我未提及的情况下额外添加符合某些国家标准要求的信息
                    """.format(content_direction, marketing_theme, appliance_type, content_description,
                               content_style, self.copy_length, self.input_language)

        return prompt

    # 实现科技的行业文案生成
    def tech_generator(self):
        marketing_theme = self.task_data.get('marketing_theme')
        brand = self.task_data.get('brand')
        scene_theme = self.task_data.get('scene_theme')
        copy_style = self.task_data.get('copy_style')
        prompt = """我是一名营销文案的策划者，现在假设你是一名科技行业的营销文案策划师，
                现在需要你围绕{}品牌的{}产品这一营销主题，基于{}的场景主题，
                保证{}的文案风格
                避免使用空泛的夸赞文案，注意用词的科学性、专业性、准确性，同时生成{}的{}营销文案。
                """.format(brand, marketing_theme, scene_theme, copy_style, self.copy_length, self.input_language)

        return prompt

    # ###################### #
    # 实现平台文案的生成         #
    # ###################### #
    # 实现小红书的平台文案生成
    def red_book_generator(self):
        if 'copy_type' not in self.task_data.keys():
            return self._red_book_title()
        return self._red_book_article()

    def _red_book_article(self):
        copy_type = self.task_data.get('copy_type')
        content_subject = self.task_data.get('content_subject')
        content_theme = self.task_data.get('content_theme')
        target_audience = self.task_data.get('target_audience')
        copy_tone = self.task_data.get('copy_tone')
        keywords = self.task_data.get('keywords')
        top_type = self.task_data.get('top_type')
        similar_topics = self.task_data.get('similar_topics')
        # 获得相应的平台样例文章
        plat_sample = self.sample('red_book')
        result = '''假设你是一名专门为小红书平台写文案的专家，你将根据我提供的信息来生成一段符合该平台风格的文案或者标题。
                            我的要求是:请以{}为文案的主体对象，以{}为生成文案的主要内容，将{}作为该文案的目标群体，
                            小红书平台当前的热点方向是"{}"，你应当思考一下如何将该热点方向与需要生成的文案形成关联，如果你认为将该热点方向融入到文案中不会使得文案变得不流畅，那么你需要将该热点方向融入到文案之中，否则就无视掉该热点方向。
                            文案的语气是{}，文案的语言是{}，并以{}为需要重点突出的关键词，文章的类别是{}, 来生成一篇小红书平台的{},要有符合小红书风格的emoji。
                            注意:使用你总结的小红书的平台风格。
                            提示:{}是指{}
                            文案的字数要求是{}。'''.format(content_subject, content_theme, target_audience,
                                                          similar_topics, copy_tone,
                                                          self.input_language, keywords, top_type, copy_type,
                                                          copy_type, self.plat_type.get(copy_type), self.copy_length)
        return [plat_sample, result]

    def _red_book_title(self):
        content_subject = self.task_data.get('content_subject')
        content_theme = self.task_data.get('content_theme')
        target_audience = self.task_data.get('target_audience')
        copy_tone = self.task_data.get('copy_tone')
        keywords = self.task_data.get('keywords')
        top_type = self.task_data.get('top_type')
        similar_topics = self.task_data.get('similar_topics')
        # 获得相应的平台样例文章
        plat_sample = self.sample('red_book')
        result = '''假设你是一名专门为小红书平台写文案标题的专家，你将根据我提供的信息来生成一段符合该平台风格的文案标题。
                            我的要求是:请以{}为文案的主体对象，以{}为生成文案的主要内容，将{}作为该文案的目标群体，
                            小红书平台当前的热点方向是"{}"，你应当思考一下如何将该热点方向与需要生成的文案标题形成关联，如果你认为将该热点方向融入到文案标题中不会使得文案变得不流畅，那么你需要将该热点方向融入到文案标题之中，否则就无视掉该热点方向。
                            文案的语气是{}，文案的语言是{}，并以{}为需要重点突出的关键词，文章的类别是{},要有符合小红书风格的emoji。
                            注意:使用你总结的小红书的平台风格。
                            注意：你只需要生成标题。'''.format(content_subject, content_theme, target_audience,
                                                             similar_topics, copy_tone,
                                                             self.input_language, keywords, top_type)
        return [plat_sample, result]

    # 实现头条的平台文案生成
    def head_generator(self):
        marketing_theme = self.task_data.get('marketing_theme')
        content_scene = self.task_data.get('content_scene')
        content_description = self.task_data.get('content_description')
        content_style = self.task_data.get('content_style')
        similar_topics = self.task_data.get('similar_topics')
        # 获得相应的平台样例文章
        plat_sample = self.sample('head')
        result = '''假设你是一名专门为百度头条平台写文案的专家，你将根据我提供的信息来生成一段符合该平台风格的文案或者标题。
                    我的要求是:请以{}为文案的主体对象，以{}为生成文案的主要内容，将{}作为该文案的内容场景，
                    头条平台当前的热点方向是"{}"，你应当思考一下如何将该热点方向与需要生成的文案形成关联，如果你认为将该热点方向融入到文案中不会使得文案变得不流畅，那么你需要将该热点方向融入到文案之中，否则就无视掉该热点方向。
                    文案的语言是{}，来生成一篇百度头条平台的{}文案。
                    注意:使用你总结的头条的平台风格，文案的字数要求是{}。
                    提示:{}是指{}'''.format(marketing_theme, content_description, content_scene, similar_topics,
                                            self.input_language,
                                            content_style,
                                            content_style, self.plat_type.get(content_style),
                                            self.copy_length)
        return [plat_sample, result]

    # 实现懂车帝的平台文案生成
    def know_generator(self):
        model = self.task_data.get('model')
        brand = self.task_data.get('brand')
        car = brand + ' ' + model
        # 从数据库获取车的信息
        try:
            msg = extract_from_db(car)
        except:
            msg = 'None'
        content_description = self.task_data.get('content_description')
        content_style = self.task_data.get('content_style')
        keywords = self.task_data.get('keywords')
        similar_topics = self.task_data.get('similar_topics')
        # 获得相应的平台样例文章
        plat_sample = self.sample('know')
        if brand in model:
            car = model
        result = '''假设你是一名专门为懂车帝平台写文案的专家，你将根据我提供的信息来生成一段符合该平台风格的文案或者标题。
                    我的要求是:请以{}为文案的主体对象，利用其的基本信息，以{}为生成文案的主要内容，并以{}为需要重点突出的关键词。
                    懂车帝平台当前的热点方向是"{}"，你应当思考一下如何将该热点方向与需要生成的文案形成关联，如果你认为将该热点方向融入到文案中不会使得文案变得不流畅，那么你需要将该热点方向融入到文案之中，否则就无视掉该热点方向。
                    文案的语言是{}，文案的字数要求是{}，来生成一篇百度头条平台的{}文案。
                    注意:使用你总结的懂车帝的平台风格。
                    提示:车的基本信息如下:{}。\n对于车的基本信息，应当合理自然的运用到文章之中，而不是简单罗列出来，与此同时你需要严格按照我提供的汽车信息完成创作，严禁使用我未提供的汽车的信息。
                    提示:{}是指{}，尽量使用第一人称，以“我”的口吻来讲述。'''.format(car, content_description, keywords,
                                                                                 similar_topics, self.input_language,
                                                                                 self.copy_length,
                                                                                 content_style, msg, content_style,
                                                                                 self.plat_type.get(content_style))
        return [plat_sample, result]

    # 实现百家的平台文案生成
    def hundred_generator(self):
        marketing_theme = self.task_data.get('marketing_theme')
        content_description = self.task_data.get('content_description')
        hot_content = self.task_data.get('hot_content')
        hot_field = self.task_data.get('hot_field')
        # 获得相应的平台样例文章
        plat_sample = self.sample('hundred')
        result = '''假设你是一名专门为百家号平台写文案的专家，你将根据我提供的信息来生成一段符合该平台风格的文案或者标题。
                    我的要求是:请以{}为文案的主体对象，以{}为生成文案的主要内容，
                    百家号平台当前的热点方向是"{}"，你应当思考一下如何将该热点方向与需要生成的文案形成关联，如果你认为将该热点方向融入到文案中不会使得文案变得不流畅，那么你需要将该热点方向融入到文案之中，否则就无视掉该热点方向。
                    文案的语言是{}，文案的字数要求是{}，来生成一篇百家号平台的{}领域的文案。
                    注意:使用你总结的百家号的平台风格。'''.format(marketing_theme, content_description, hot_content,
                                                                 self.input_language, self.copy_length, hot_field)
        return [plat_sample, result]

    # 实现汽车之家的平台文案生成
    def car_home_generator(self):
        model = self.task_data.get('model')
        brand = self.task_data.get('brand')
        car = brand + ' ' + model
        # 从数据库获取车的信息
        try:
            msg = extract_from_db(car)
        except:
            msg = 'None'
        content_description = self.task_data.get('content_description')
        writing_type = self.task_data.get('writing_type')
        # 获得相应的平台样例文章
        plat_sample = self.sample('car_home')
        if brand in model:
            car = model
        result = '''假设你是一名专门为汽车之家平台写文案的专家，你将根据我提供的信息来生成一段符合该平台风格的文案或者标题。
                    我的要求是:请以{}为文案的主体对象，利用其的基本信息，以{}为生成文案的主要内容，
                    文案的语言是{}，文案的字数要求是{}，来生成一篇汽车之家平台的{}文案。
                    注意使用你总结的汽车之家的平台风格。
                    提示:车的基本信息如下:{}\n对于车的基本信息，应当合理自然的运用到文章之中，而不是简单罗列出来，与此同时你需要严格按照我提供的汽车信息完成创作，严禁使用我未提供的汽车的信息。
                    提示:{}是指{}'''.format(car, content_description, self.input_language, self.copy_length,
                                            writing_type, msg,
                                            writing_type, self.plat_type.get(writing_type))
        return [plat_sample, result]

    # ###################### #
    # 实现市场文案的生成         #
    # ###################### #
    # 实现营销节点推广的文案生成
    def marketing_node_generator(self):
        marketing_theme = self.task_data.get('marketing_theme')
        marketing_node = self.task_data.get('marketing_node')
        copy_type = self.task_data.get('copy_type')
        copy_style = self.task_data.get('copy_style')
        prompt = """假设你是一名营销文案策划师，
                现在需要你围绕{}这一营销主题，在{}这一营销节点，生成{}类型的文案，保证{}的文案风格
                避免使用空泛的夸赞文案，要求生成{}的{}节点推广营销文案。
                注意不要添加我未曾提及的活动信息或商品的详细信息。
                """.format(marketing_theme, marketing_node, copy_type, copy_style, self.copy_length,
                           self.input_language)

        return prompt

    # 实现公司介绍的文案生成
    def company_intro_generator(self):
        company_name = self.task_data.get('company_name')
        industry = self.task_data.get('industry')
        key_information = self.task_data.get('key_information')
        prompt = """假设你是一名文案策划师，
                现在需要你围绕{}这一公司，其属于{}这一行业，围绕以下关键信息:{},
                避免使用空泛的夸赞文案，生成{}的{}广告标语文案，需要注意不要在关键信息未提及的情况下，添加额外的实际信息，保证真实性。
                同时对于关键信息中含义不明的缩写性关键词，注意阐明其含义。
                """.format(company_name, industry, key_information, self.copy_length, self.input_language)

        return prompt

    # 实现广告slogan的文案生成
    def advertise_slogan_generator(self):
        marketing_theme = self.task_data.get('marketing_theme')
        scene_category = self.task_data.get('scene_category')
        slogan_style = self.task_data.get('slogan_style')
        prompt = """假设你是一名广告文案策划师，
                现在需要你围绕{}这一营销主题，其从属{}这一内容分类，生成{}风格的广告标语,
                避免使用空泛的夸赞文案，生成多条{}广告标语文案，需要注意不要在关键信息未提及的情况下，添加额外的实际信息，保证真实性。
                请注意你的返回内容只需包括标语，不要有其他提示性语言。
                """.format(marketing_theme, scene_category, slogan_style, self.input_language)

        return prompt

    # 实现品牌介绍的文案生成
    def brand_intro_generator(self):
        brand_introduction = self.task_data.get('brand_introduction')
        product_type = self.task_data.get('product_type')
        industry = self.task_data.get('industry')
        copy_tone = self.task_data.get('copy_tone')
        prompt = """假设你是一名文案策划师，现在需要你生成品牌介绍的文案，
                需要你围绕{}这一品牌的简短介绍，这一品牌所提供的产品或服务的类别为{}，其所属行业为{},要求文案的风格或调性为{},
                避免使用空泛的夸赞文案，生成{}的{}广告标语文案，需要注意不要在关键信息未提及的情况下，添加额外的实际信息，保证真实性。
                """.format(brand_introduction, product_type, industry, copy_tone, self.copy_length, self.input_language)

        return prompt

    # 实现ip形象介绍的文案生成
    def ip_image_generator(self):
        brand_name = self.task_data.get('brand_name')
        main_product = self.task_data.get('main_product')
        ip_name = self.task_data.get('ip_name')
        copy_tone = self.task_data.get('copy_tone')
        prompt = """假设你是一名文案策划师，现在需要你生成介绍某品牌ip形象的文案，
                品牌名称为{}，这一品牌所提供的主要产品为{}，这一品牌的ip形象为{},要求文案的风格或调性为{},
                避免使用空泛的夸赞文案，生成{}的{}品牌ip形象介绍文案，
                注意品牌和ip形象的衔接要自然，不要过于生硬。
                """.format(brand_name, main_product, ip_name, copy_tone, self.copy_length, self.input_language)

        return prompt

    # ###################### #
    # 实现视频文案的生成         #
    # ###################### #
    # 实现AI短视频编剧的文案生成
    def ai_generator(self):
        video_theme = self.task_data.get('video_theme')
        copy_type = self.task_data.get('copy_type')
        copy_tone = self.task_data.get('copy_tone')
        prompt = """假设你是一名文案策划师，现在需要你生成AI短视频编剧的文案，
                        要求:视频的核心内容为{}，文案的类型为{}，文案的语气为{},
                        避免使用空泛的夸赞文案，文案的语言为{}，文案的长度为{},
                        注意衔接要自然，不要过于生硬。
                        """.format(video_theme, copy_type, copy_tone, self.input_language, self.copy_length)
        return prompt

    # 实现视频逐字稿的文案生成
    def video_generator(self):
        marketing_theme = self.task_data.get('marketing_theme')
        content_scene = self.task_data.get('content_scene')
        script_type = self.task_data.get('script_type')
        video_theme = self.task_data.get('video_theme')
        prompt = """假设你是一名文案策划师，现在需要你生成视频逐字稿的文案，
                                要求:视频的营销主题为{}，视频的内容场景为{}，视频的类型为{},视频要传达的主题为{}，
                                避免使用空泛的夸赞文案，文案的语言为{}，文案的长度为{},
                                注意衔接要自然，不要过于生硬。
                                """.format(marketing_theme, content_scene, script_type, video_theme,
                                           self.input_language, self.copy_length)
        return prompt

    # 视频营销灵感
    def inspire_generator(self):
        marketing_theme = self.task_data.get('marketing_theme')
        video_type = self.task_data.get('video_type')
        video_theme = self.task_data.get('video_theme')
        prompt = """假设你是一名文案策划师，现在需要你生成视频营销灵感的文案，
                                要求:视频要强调的营销主题为{}，视频的类型为{}，视频要传达的信息为{},
                                避免使用空泛的夸赞文案，文案的语言为{}，文案的长度为{},
                                注意衔接要自然，不要过于生硬。
                                """.format(marketing_theme, video_type, video_theme, self.input_language,
                                           self.copy_length)
        return prompt

    # 分镜脚本
    def shoot_script_generator(self):
        marketing_theme = self.task_data.get('marketing_theme')
        video_type = self.task_data.get('video_type')
        content_description = self.task_data.get('content_description')
        prompt = """假设你是一名文案策划师，现在需要你生成分镜脚本的文案，
                                        要求:视频要强调的营销主题为{}，视频的类型为{}，视频的主要内容为{},
                                        避免使用空泛的夸赞文案，文案的语言为{}，文案的长度为{},
                                        注意衔接要自然，不要过于生硬。
                                        """.format(marketing_theme, video_type, content_description,
                                                   self.input_language,
                                                   self.copy_length)
        return prompt

    # 拍摄剧本
    def shoot_generator(self):
        marketing_theme = self.task_data.get('marketing_theme')
        video_type = self.task_data.get('video_type')
        script_type = self.task_data.get('script_type')
        plot_style = self.task_data.get('plot_style')
        content_description = self.task_data.get('content_description')
        prompt = """假设你是一名文案策划师，现在需要你生成分镜脚本的文案，
                                    要求:视频要强调的营销主题为{}，视频的类型为{}，剧本的类型为{},剧本的风格为{}，剧本的简要内容为{}，
                                    避免使用空泛的夸赞文案，文案的语言为{}，文案的长度为{},
                                    注意衔接要自然，不要过于生硬。
                                    """.format(marketing_theme, video_type, content_description, script_type,
                                               plot_style,
                                               self.input_language, self.copy_length)
        return prompt

    # 视频拍摄大纲
    def video_abstract_generator(self):
        marketing_theme = self.task_data.get('marketing_theme')
        video_type = self.task_data.get('video_type')
        video_topic = self.task_data.get('video_topic')
        prompt = """假设你是一名文案策划师，现在需要你生成视频拍摄大纲的文案，
                                    要求:视频要强调的营销主题为{}，视频的类型为{}，视频的主要主题为{},
                                    避免使用空泛的夸赞文案，文案的语言为{}，文案的长度为{},
                                    注意衔接要自然，不要过于生硬。
                                    """.format(marketing_theme, video_type, video_topic,
                                               self.input_language, self.copy_length)
        return prompt

    # 企业宣传片脚本
    def publicize_generator(self):
        organization_name = self.task_data.get('organization_name')
        organization_type = self.task_data.get('organization_type')
        industry = self.task_data.get('industry')
        vision = self.task_data.get('vision')
        prompt = """假设你是一名文案策划师，现在需要你生成企业宣传片脚本的文案，
                                    要求:视频所宣传的企业为{}，企业的类型为{}，企业所属的行业为{},企业的景愿为{}，
                                    避免使用空泛的夸赞文案，文案的语言为{}，文案的长度为{},
                                    注意衔接要自然，不要过于生硬。
                                    """.format(organization_name, organization_type, industry, vision,
                                               self.input_language, self.copy_length)
        return prompt

    # 直播脚本
    def live_generator(self):
        product = self.task_data.get('product')
        industry = self.task_data.get('industry')
        product_description = self.task_data.get('product_description')
        script_type = self.task_data.get('script_type')
        core_selling_points = self.task_data.get('core_selling_points')
        prompt = """假设你是一名文案策划师，现在需要你生成直播脚本的文案，
                                    要求:直播中要推广或展示的产品为{}，产品所属的行业为{}，产品的简要描述为{},脚本的类型为{}，产品的核心优势为{}，
                                    避免使用空泛的夸赞文案，文案的语言为{}，文案的长度为{},
                                    注意衔接要自然，不要过于生硬。
                                    """.format(product, industry, product_description, script_type, core_selling_points,
                                               self.input_language, self.copy_length)
        return prompt

    # ###################### #
    # 实现媒体文案的生成         #
    # ###################### #
    # 时事政治
    def politics_generator(self):
        copy_theme = self.task_data.get('copy_theme')
        copy_scene = self.task_data.get('copy_scene')
        content_description = self.task_data.get('content_description')
        copy_style = self.task_data.get('copy_style')
        prompt = """假设你是一名文案策划师，现在需要你生成时事政治的文案，
                                    要求:文案所关注的主题为{}，文本适用于的场景为{}，文本的主要内容为{},文本的风格为{}，
                                    避免使用空泛的夸赞文案，文案的语言为{}，文案的长度为{},
                                    注意衔接要自然，不要过于生硬。
                                    """.format(copy_theme, copy_scene, content_description, copy_style,
                                               self.input_language, self.copy_length)
        return prompt

    # 商业新闻
    def commercial_generator(self):
        copy_theme = self.task_data.get('copy_theme')
        copy_scene = self.task_data.get('copy_scene')
        content_description = self.task_data.get('content_description')
        copy_style = self.task_data.get('copy_style')
        prompt = """假设你是一名文案策划师，现在需要你生成商业新闻的文案，
                                    要求:文案所关注的主题为{}，文本适用于的场景为{}，文本的主要内容为{},文本的风格为{}，
                                    避免使用空泛的夸赞文案，文案的语言为{}，文案的长度为{},
                                    注意衔接要自然，不要过于生硬。
                                    """.format(copy_theme, copy_scene, content_description, copy_style,
                                               self.input_language, self.copy_length)
        return prompt

    # 科技新闻
    def technology_generator(self):
        copy_theme = self.task_data.get('copy_theme')
        copy_scene = self.task_data.get('copy_scene')
        content_description = self.task_data.get('content_description')
        copy_style = self.task_data.get('copy_style')
        prompt = """假设你是一名文案策划师，现在需要你生成科技新闻的文案，
                                    要求:文案所关注的主题为{}，文本适用于的场景为{}，文本的主要内容为{},文本的风格为{}，
                                    避免使用空泛的夸赞文案，文案的语言为{}，文案的长度为{},
                                    注意衔接要自然，不要过于生硬。
                                    """.format(copy_theme, copy_scene, content_description, copy_style,
                                               self.input_language, self.copy_length)
        return prompt

    # 体育新闻
    def PE_generator(self):
        copy_theme = self.task_data.get('copy_theme')
        copy_scene = self.task_data.get('copy_scene')
        content_description = self.task_data.get('content_description')
        copy_style = self.task_data.get('copy_style')
        prompt = """假设你是一名文案策划师，现在需要你生成体育新闻的文案，
                                    要求:文案所关注的主题为{}，文本适用于的场景为{}，文本的主要内容为{},文本的风格为{}，
                                    避免使用空泛的夸赞文案，文案的语言为{}，文案的长度为{},
                                    注意衔接要自然，不要过于生硬。
                                    """.format(copy_theme, copy_scene, content_description, copy_style,
                                               self.input_language, self.copy_length)
        return prompt

    # 娱乐新闻
    def entertainment_generator(self):
        copy_theme = self.task_data.get('copy_theme')
        copy_scene = self.task_data.get('copy_scene')
        content_description = self.task_data.get('content_description')
        copy_style = self.task_data.get('copy_style')
        prompt = """假设你是一名文案策划师，现在需要你生成娱乐新闻的文案，
                                    要求:文案所关注的主题为{}，文本适用于的场景为{}，文本的主要内容为{},文本的风格为{}，
                                    避免使用空泛的夸赞文案，文案的语言为{}，文案的长度为{},
                                    注意衔接要自然，不要过于生硬。
                                    """.format(copy_theme, copy_scene, content_description, copy_style,
                                               self.input_language, self.copy_length)
        return prompt

    # 财经通讯
    def financial_generator(self):
        industry = self.task_data.get('industry')
        central_idea = self.task_data.get('central_idea')
        prompt = """假设你是一名文案策划师，现在需要你生成财经通讯的文案，
                                    要求:文本需要关注的特定行业为{}，文本的核心主题为{}，
                                    避免使用空泛的夸赞文案，文案的语言为{}，文案的长度为{},
                                    注意衔接要自然，不要过于生硬。
                                    """.format(industry, central_idea,
                                               self.input_language, self.copy_length)
        return prompt
