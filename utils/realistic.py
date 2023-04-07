import random


def get_random_prompt():
    mushroom_varieties = ['white agaricus', 'brown', 'white stained agaricus', 'white dirty agaricus',
                          'white agaricus mushrooms with dirt',
                          'white portabello', 'portabello', 'hedgehog',
                          'shiitake', 'porcini', 'chanterelle']  # 'maitake', 'morel'
    mushroom_varieties_w = (25, 5, 15, 5, 5, 5, 5, 10, 5, 10, 10)
    a = random.choices(mushroom_varieties, weights=mushroom_varieties_w, k=1)

    help0 = ['on', 'in']
    b = random.choices(help0, k=1)

    grounds = ['dark brown soil ground', 'dark soil ground', 'brown soil ground', 'black soil ground',
               'brown soil', 'dark soil', 'black soil',
               'green grass', 'green ground', 'green field', 'grass']
    grounds_w = (30, 5, 5, 5, 5, 5, 5, 15, 5, 10, 10)
    c = random.choices(grounds, weights=grounds_w, k=1)

    help1 = ['with', 'and']
    d = random.choices(help1, k=1)

    background = ['sky', 'forest', 'dark sky', 'green forest', 'trees', 'green trees',
                  'sky and clouds', 'sky and stars', 'garden', 'deep forest', 'farm',
                  'grains', 'golden grains']
    e = random.choices(background, k=1)

    help2 = ['as a background', 'in the back']
    f = random.choices(help2, k=1)

    prompt = a[0] + ' mushrooms ' + b[0] + ' ' + c[0] + ' ' + d[0] + ' ' + e[0] + ' ' + f[0]
    print(prompt)
    return prompt


def get_random_params():
    seed = random.randint(0, 2147483647)
    strength = round(random.uniform(0.70, 1.00), 2)
    scale = round(random.uniform(9.0, 12.0), 1)
    prompt = get_random_prompt()
    return seed, strength, scale, prompt
