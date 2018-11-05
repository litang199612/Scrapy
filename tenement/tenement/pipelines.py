# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3
# db = sqlite3.connect("./../tenement.db")
# cursor = db.cursor()
from fontTools.ttLib import TTFont


def font_parse(text):
    """
    解析乱码的数字
    :param rental:
    :param house_type:
    :param toward_floor:
    :return:
    """
    decryption_text = ""
    for alpha in text:
        hex_alpha = alpha.encode('unicode_escape').decode()[2:]
        if len(hex_alpha) == 4:
            one_font = int(hex_alpha, 16)
            font = TTFont('base.woff')
            font_dict = font['cmap'].tables[2].ttFont.tables['cmap'].tables[1].cmap
            b = font['cmap'].tables[2].ttFont.getReverseGlyphMap()
            if one_font in font_dict.keys():
                gly_font = font_dict[one_font]
                item_text = str(b[gly_font] - 1)
            else:
                item_text = alpha

        else:
            item_text = alpha
        decryption_text += item_text
    return decryption_text


class TenementPipeline(object):
    def __init__(self):
        self.conn = sqlite3.connect("./../tenement.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("create table IF NOT EXISTS house(rental, lease_way, house_type, toward_floor, housing_estate, region, address, url);")
        self.conn.commit()

    def process_item(self, item, spider):
        if not str(item["rental"]).isdecimal():
            item["rental"] = font_parse(item["rental"])
            item["house_type"] = font_parse(item["house_type"])
            item["toward_floor"] = font_parse(item["toward_floor"])

        sql_str = "INSERT INTO house VALUES ('" +item["rental"]+"','" +item["lease_way"]+"','" +item["house_type"]+"','" +item["toward_floor"]+"','" +item["housing_estate"]+"','" +item["region"]+"','" +item["address"]+"','" +item["url"] +"')"
        self.cursor.execute(sql_str)
        self.conn.commit()
        return item
