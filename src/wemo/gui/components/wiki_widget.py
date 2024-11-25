from PySide6.QtWidgets import (
    QLabel,
    QWidget,
    QVBoxLayout,
    QPlainTextEdit,
)

readme = """<h1>使用指南</h1>

<h2>日常使用</h2>
<ol>
  <li>框选「同步数据」 、「更新数据」、「导出」。</li>
  <li>点击「启动」按钮，等待进度条完成。</li>
  <li>点击「浏览器打开」按钮，查看导出的数据。</li>
</ol>

<h2>FAQ</h2>
<h3>本软件的原理是什么？</h3>
<p>
  对微信的本地缓存数据（包括图片，视频，头像）进行持久化保存，然后通过浏览器进行展示。
</p>
<br />

<h3>为什么不能显示最新朋友圈？</h3>
<p>需要关闭微信后再登录，然后打开本软件。</p>
<br />

<h3>右上角的警告信息是什么意思？</h3>
<p>
  需要在朋友圈浏览该朋友圈，让微信在本地进行缓存。<br />
  具体方法参加【如何需要在电脑中浏览特定联系人的朋友圈？】
</p>
<br />

<h3>如何需要在电脑中浏览特定联系人的朋友圈？</h3>
<ul>
  <li>
    点击「同步数据」，选择「朋友圈」，输入 1 （随便什么都行），然后点击「搜索」
  </li>
  <li>点击「朋友」，选择特定联系人，然后在搜索框输入「？」（⚠️注意是中文）</li>
  <li>浏览朋友圈</li>
</ul>
"""


class WikiWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.abstract_label = QLabel("使用指南", self)
        self.readme = QPlainTextEdit(self)
        self.readme.setReadOnly(True)
        self.readme.appendHtml(readme)

        layout.addWidget(self.abstract_label)
        layout.addWidget(self.readme)
        self.setLayout(layout)
