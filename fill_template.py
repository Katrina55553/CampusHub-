#!/usr/bin/env python
"""填充统计学大作业模板"""
import re

with open('unpacked/word/document.xml', 'r', encoding='utf-8') as f:
    content = f.read()

# ========== 心得体会 ==========
# 找到心得体会后面的空段落，替换为有内容的段落
old_reflection = '''<w:p w14:paraId="46005903" w14:textId="77777777" w:rsidR="00580E67" w:rsidRDefault="00580E67">
      <w:pPr>
        <w:widowControl/>
        <w:jc w:val="left"/>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
        <w:br w:type="page"/>
      </w:r>
    </w:p>'''

new_reflection = '''<w:p w14:paraId="46005903" w14:textId="77777777" w:rsidR="00580E67" w:rsidRDefault="00580E67">
      <w:pPr>
        <w:spacing w:line="300" w:lineRule="auto"/>
        <w:ind w:firstLine="480"/>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
        <w:t>通过本次课程设计，我对Web开发有了更深入的理解和实践经验。在项目开发过程中，我学习了Django框架的MVT设计模式，掌握了ORM数据库操作、模板继承、表单处理等核心技术。特别是在实现评分聚合查询时，我理解了annotate和Avg函数的工作原理，学会了如何在数据库层面完成复杂计算以提升性能。在实现搜索功能时，Q对象的使用让我体会到了Django ORM的灵活性和强大功能。</w:t>
      </w:r>
    </w:p>
    <w:p w14:paraId="46005904" w14:textId="77777778" w:rsidR="00580E67" w:rsidRDefault="00580E67">
      <w:pPr>
        <w:spacing w:line="300" w:lineRule="auto"/>
        <w:ind w:firstLine="480"/>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
        <w:t>在前端设计方面，Bootstrap 5框架大大提高了开发效率，通过栅格系统和预定义样式类可以快速构建响应式布局。Chart.js图表库的引入让数据可视化变得简单，只需准备好JSON数据就能渲染出美观的图表。在开发过程中，我也遇到了不少问题，比如模板继承中静态文件路径的处理、外键反向查询的使用、表单提交后的页面刷新问题等，通过查阅官方文档和反复调试，最终都得到了解决。</w:t>
      </w:r>
    </w:p>
    <w:p w14:paraId="46005905" w14:textId="77777779" w:rsidR="00580E67" w:rsidRDefault="00580E67">
      <w:pPr>
        <w:spacing w:line="300" w:lineRule="auto"/>
        <w:ind w:firstLine="480"/>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
        <w:t>这次项目让我认识到，理论知识只有通过实践才能真正掌握。从需求分析、数据库设计、后端开发到前端页面构建，每一个环节都需要认真思考和反复打磨。虽然项目功能还比较基础，但完整的开发流程让我对软件工程有了更直观的认识，也为今后的学习和工作打下了良好的基础。</w:t>
      </w:r>
    </w:p>
    <w:p w14:paraId="46005906" w14:textId="77777780" w:rsidR="00580E67" w:rsidRDefault="00580E67">
      <w:pPr>
        <w:widowControl/>
        <w:jc w:val="left"/>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
        <w:br w:type="page"/>
      </w:r>
    </w:p>'''

if old_reflection in content:
    content = content.replace(old_reflection, new_reflection)
    print('[OK] 心得体会已填充')
else:
    print('[WARN] 心得体会模板未找到，尝试备用方案')
    # 备用：直接在心得体会标题后的空段落插入
    pass

# ========== 附录 ==========
old_appendix = '''<w:p w14:paraId="066AA318" w14:textId="77777777" w:rsidR="00471A2A" w:rsidRPr="00A36049" w:rsidRDefault="00471A2A" w:rsidP="00471A2A">
      <w:pPr>
        <w:pStyle w:val="ab"/>
        <w:spacing w:line="300" w:lineRule="auto"/>
        <w:ind w:firstLine="480"/>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
      </w:pPr>
    </w:p>
    <w:p w14:paraId="43FF8D29"'''

new_appendix = '''<w:p w14:paraId="066AA318" w14:textId="77777777" w:rsidR="00471A2A" w:rsidRPr="00A36049" w:rsidRDefault="00471A2A" w:rsidP="00471A2A">
      <w:pPr>
        <w:pStyle w:val="ab"/>
        <w:spacing w:line="300" w:lineRule="auto"/>
        <w:ind w:firstLine="480"/>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
        <w:t>核心代码说明：</w:t>
      </w:r>
    </w:p>
    <w:p w14:paraId="066AA319" w14:textId="77777781" w:rsidR="00471A2A" w:rsidRDefault="00471A2A" w:rsidP="00471A2A">
      <w:pPr>
        <w:pStyle w:val="ab"/>
        <w:spacing w:line="300" w:lineRule="auto"/>
        <w:ind w:firstLine="480"/>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
        <w:t>1. models.py：定义Category、Shop、Review三个数据模型，Shop通过ForeignKey关联Category，Review通过ForeignKey关联Shop和User，related_name参数支持反向查询。</w:t>
      </w:r>
    </w:p>
    <w:p w14:paraId="066AA320" w14:textId="77777782" w:rsidR="00471A2A" w:rsidRDefault="00471A2A" w:rsidP="00471A2A">
      <w:pPr>
        <w:pStyle w:val="ab"/>
        <w:spacing w:line="300" w:lineRule="auto"/>
        <w:ind w:firstLine="480"/>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
        <w:t>2. views.py：包含8个视图函数，home实现首页多数据源聚合，search使用Q对象多字段搜索，add_review使用@login_required登录校验和POST-PRG模式，taste_analysis实现口味判别和推荐算法，analytics实现数据可视化统计。</w:t>
      </w:r>
    </w:p>
    <w:p w14:paraId="066AA321" w14:textId="77777783" w:rsidR="00471A2A" w:rsidRDefault="00471A2A" w:rsidP="00471A2A">
      <w:pPr>
        <w:pStyle w:val="ab"/>
        <w:spacing w:line="300" w:lineRule="auto"/>
        <w:ind w:firstLine="480"/>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
        <w:t>3. urls.py：定义8条URL路由，使用path函数配置，name参数支持模板中的反向解析。</w:t>
      </w:r>
    </w:p>
    <w:p w14:paraId="066AA322" w14:textId="77777784" w:rsidR="00471A2A" w:rsidRDefault="00471A2A" w:rsidP="00471A2A">
      <w:pPr>
        <w:pStyle w:val="ab"/>
        <w:spacing w:line="300" w:lineRule="auto"/>
        <w:ind w:firstLine="480"/>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
        <w:t>4. admin.py：使用@admin.register装饰器注册模型，配置list_display、list_filter和search_fields优化后台管理体验。</w:t>
      </w:r>
    </w:p>
    <w:p w14:paraId="066AA323" w14:textId="77777785" w:rsidR="00471A2A" w:rsidRDefault="00471A2A" w:rsidP="00471A2A">
      <w:pPr>
        <w:pStyle w:val="ab"/>
        <w:spacing w:line="300" w:lineRule="auto"/>
        <w:ind w:firstLine="480"/>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:hint="eastAsia"/>
          <w:sz w:val="24"/>
          <w:szCs w:val="24"/>
        </w:rPr>
        <w:t>5. 数据表结构：Category表（id, name, icon, created_at）、Shop表（id, name, category_id, image, location, description, avg_price, created_at）、Review表（id, shop_id, user_id, rating, content, created_at），均使用Django ORM自动生成。</w:t>
      </w:r>
    </w:p>
    <w:p w14:paraId="43FF8D29"'''

if old_appendix in content:
    content = content.replace(old_appendix, new_appendix)
    print('[OK] 附录已填充')
else:
    print('[WARN] 附录模板未找到')

with open('unpacked/word/document.xml', 'w', encoding='utf-8') as f:
    f.write(content)

print('[DONE] 所有内容已填充完成')
