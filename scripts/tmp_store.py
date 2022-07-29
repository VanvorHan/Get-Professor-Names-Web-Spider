arr = [("https://power.seu.edu.cn/9232/list.htm", "能源工程系", 4),
        ("https://power.seu.edu.cn/dlgcjzdhx/list.htm", "动力工程及自动化系", 3),
        ("https://power.seu.edu.cn/9244/list.htm", "制冷与建筑环境系", 2),
        ("https://power.seu.edu.cn/9248/list.htm", "环境科学与工程系", 3),
        ("https://power.seu.edu.cn/hkxyjsx/list.htm", "核科学与技术系", 1)]
for faculty in arr:
    link = faculty[0]
    faculty_name = faculty[1]
    page_count = faculty[2]
    for page in range(1,page_count+1):
        data_dic_str = '''siteId: 31
        pageIndex: ''' + str(page) + '''
        rows: 16
        conditions: [{"orConditions":[{"field":"academicDegree","value":"%''' + faculty_name + '''%","judge":"like"},{"field":"finalEducation","value":"%''' + faculty_name + '''%","judge":"like"}]},{"field":"language","value":1,"judge":"="},{"field":"published","value":1,"judge":"="}]
        orders: [{"field":"letter","type":"asc"}]
        returnInfos: [{"field":"title","name":"title"},{"field":"headerPic","name":"headerPic"},{"field":"degree","name":"degree"},{"field":"finalEducation","name":"finalEducation"},{"field":"department","name":"department"},{"field":"graduationSchool","name":"graduationSchool"},{"field":"discipline","name":"discipline"},{"field":"address","name":"address"},{"field":"cnUrl","name":"cnUrl"}]
        articleType: 1
        level: 1
        '''