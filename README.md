# Scrapy 抓取知乎用户信息

## 项目使用方法

1. 克隆项目

    ```shell
    git clone https://github.com/Annihilater/zhihuuser.git
    ```

2. 安装依赖

    ```shell
    pip install -r requirements.txt
    ```

3. 本机启动 MongoDB 数据库

4. 运行爬虫

    ```shell
    scrapy crawl zhihu
    ```

5. 然后就会在 MongoDB 的图形化客户端看到
    ![image-20191024173110932](https://klause-blog-pictures.oss-cn-shanghai.aliyuncs.com/2019-10-24-093111.png)

## 思路

1. 选择起始人：大 V
2. 获取它的粉丝和关注列表：通过知乎接口
3. 获取用户信息列表：通过知乎接口获取列表中每位用户的详细信息
4. 获取每位用户粉丝和关注列表：进一步获取列表中的每一位用户的详细信息，实现递归爬取

 

## 项目实战

### 爬虫

- `start_requests`方法
    1. 获取用户信息
    2. 获取该用户的关注列表
    3. 获取该用户的粉丝列表
- `parse_user`方法
    1. 解析用户的详细信息，返回 `item` 给 `Pipline`
    2. 获取用户的关注列表，进行下一步递归调用
    3. 获取用户的粉丝列表，进行下一步递归调用
- `parse_follows`方法
    1. 解析**关注列表**或者**粉丝列表**，获取 `url_token`，再通过 `url_token`获取用户详细信息，进行递归调用
    2. 对**关注列表**或者**粉丝列表**递归进行分页

## 数据存储

使用 MongoDB 数据库进行用户信息存储，使用的是官方示例代码，唯一改动的是将**数据插入操作**改成了**数据更新操作**。

```python
def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item
```

改成

```python
    def process_item(self, item, spider):
        self.db[self.collection_name].update_one({'url_token': item['url_token']}, {'$set': item}, True)
        return item
```

使用 `update_one`语句：

 先去数据库中依据 `url_token` 查找 `item`，如果找到了则更新 `item`，如果找不到，则插入 `item`

```python
update_one(filter, update, upsert=False, bypass_document_validation=False, collation=None, array_filters=None, session=None)
```

参数解释：

`filter`：查询条件，`{'url_token': item['url_token']}`依据 `url_token`查询

`update`：插入信息，`{'$set': item}`

`upsert`：如果没有查询到数据，是否执行插入操作


