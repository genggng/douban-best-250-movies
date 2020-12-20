from py2neo import Graph,Node,Relationship
import argparse
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--number', default=5, help='movies number to be created knoeledge graph')
args = parser.parse_args()
movie_number = int(args.number)    #修改这个变量，来控制生成图的大小。最多用250个电影生成图

df = pd.read_excel("douban_best250_movies.xls")
df = df.iloc[:movie_number]

actors = []
types = []
# 字符串分割为列表
df["演员"] = df["演员"].apply(lambda s: s.split('/'))
df["类型"] = df["类型"].apply(lambda s: s.split('/'))
for index in range(len(df)):
    actors += df.loc[index,"演员"]
    types += df.loc[index,"类型"]
# 将四类顶点提取出来，用集合存储
actors = set(actors)
types = set(types)
names = set(df["名称"])
directors = set(df["导演"])

#连接数据库
graph = Graph("bolt://localhost:7687",username="neo4j",password="123456")
graph.delete_all()   #每次先清空数据库

# 创建4类节点： 电影名，导演，演员，电影类型
name_nodes = {}
director_nodes = {}
actor_nodes = {}
type_nodes = {}
for name in names:
    node = Node('Movie',name=name)
    graph.create(node)
    name_nodes[name] = node

for director in directors:
    node = Node('Director',name=director)
    graph.create(node)
    director_nodes[director] = node

for actor in actors:
    node = Node('Actor',name=actor)
    graph.create(node)
    actor_nodes[actor] = node

for type in types:
    node = Node('Type',name=type)
    graph.create(node)
    type_nodes[type] = node


# 创建3类边：导演（导演->电影名），出演（演员->电影名），类型（电影名->类型）
for index in range(len(df)):
    name = df.loc[index,"名称"]
    director = df.loc[index,"导演"]
    actors = df.loc[index,"演员"]
    types = df.loc[index,"类型"]

    graph.create(Relationship(director_nodes[director],"导演",name_nodes[name]))
    for actor in actors:
        graph.create(Relationship(actor_nodes[actor],"出演",name_nodes[name]))

    for type in types:
        graph.create(Relationship(name_nodes[name],"类型",type_nodes[type]))
