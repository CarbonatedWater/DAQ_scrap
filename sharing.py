from datetime import timedelta
from typing import Text
from notion.client import NotionClient
from notion.block import SubheaderBlock, SubsubheaderBlock, TextBlock, DividerBlock, ImageBlock


client = NotionClient(token_v2="8a6c8ea734452ae295c450fc52f221e473fad8b1cd1cf8013a0883dd81b5936c18c3cea29e3e1df94df2dc584ab0712479e30d38cc3975b1dcd948e86b0869b71d5c8cb74cfe6c0f1d3562f64731")
client.current_user
client.session.close()

page = client.get_block('https://www.notion.so/blime/4d854cfa1e3348f9b4937660dc877f5a')
page.title = "구마교회 그 베일을 벗다! / 인간사육과 대안교육!"
page.children
page.children.add_new(SubheaderBlock, title="스포트라이트")
page.children.add_new(SubheaderBlock, title="JTBC", color="pink")
page.children.add_new(SubsubheaderBlock, title="방영일시: 2021-01-16 오후 7시 40분 [272회]", color="grey")
page.children.add_new(DividerBlock)
page.children.add_new(ImageBlock, link="https://fs.jtbc.joins.com/joydata/CP00000001/prog/preview/jtbcspotlight/img/20210114_143952_805_1.jpg.tn640.jpg")
page.children[-1].remove()

page.children.add_new(TextBlock, title="test2", color="red")

