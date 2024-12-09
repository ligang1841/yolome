from lxml import etree


def read_xml(xml_file):
    tree = etree.parse(xml_file)
    root = tree.getroot()
    return root

    #tree = etree.ElementTree.parse(in_path)
    #root = tree.getroot()
    #return root


# ---roi.xml---------------------------------------------------------------------------
'''
<patient name="p-name">
  <img name="8x1.jpg">
    <roi x="220" y="200" w="70" h="70" types="1"/>
	<roi x="920" y="190" w="130" h="90" types="2"/>
	<roi x="920" y="40" w="90" h="90" types="3"/>
  </img>
  
  ... # more img labels

</patient>
'''


def create_roi(pname):
    root = etree.Element('patient',name=pname)
    return root

### number is image number, coor is x,y
def add_roi_imgname(root,imgname,number='',coorx='0',coory='0',mn=0):
    img_node = etree.SubElement(root,'img', name=imgname)
    img_node.set('number',number)
    img_node.set('coor',coorx + ',' + coory)
    if mn>=0:
        img_node.set('mn',str(mn))
    return img_node

def add_roi_img_roi(img_xml,axis,tp,mn=0):
    roi = etree.SubElement(img_xml,'roi')
    roi.set('x', str(axis[0]))
    roi.set('y', str(axis[1]))
    roi.set('w', str(axis[2]-axis[0]))
    roi.set('h', str(axis[3]-axis[1]))
    roi.set('types',tp)
    if mn>0:
        roi.set('mn', str(mn))
    #roi.set('axis',coor)


# ---rois.xml---------------------------------------------------------------------------

#<case name="case_one">
#  <img name="00122.jpg" type="lymph" score=”0.88” slide="0" loc=”126.9, 292.3” />

def create_rois(case_name):
    root = etree.Element('case',name=case_name)
    return root

def add_sm_img(root,iname,tp,score,slide,x,y):
    img = etree.SubElement(root,'img')
    img.set('name', iname)
    img.set('type', tp)
    img.set('score',str(round(score,2)))
    img.set('slide',str(slide))
    img.set('loc',  str(round(x,1)) + ',' + str(round(y,1)))
    


# ---report.xml---------------------------------------------------------------------------
'''
<xml>
  <baseinfo>
    <pname>张三</pname>
    <pid>00020190102008</pid>
    <hid>xm937463888</hid>
    <dept>体检中心</dept>
    <bar_code>09866388</bar_code>
    <app_doctor>dr</app_doctor>				#申请医生，可空
	<app_time>2020-01-22 15:30</app_time>	#申请时间	
  	<sampling_time>2020-01-22 15:40</sampling_time>	#采样时间
	<test_item>微核</test_item>
	<age>22</age>
	<sex>1</sex>
  </baseinfo>
  <aerial_view img="aerial.jpg"/>
  <mc>
    <img>0_1_45_78_128_128.jpg</img>
    <img>2_5_33_456_128_128.jpg</img>
  </mc>
  <calc>
    <mc_num>450</mc_num>
    <lymph_num>1066</lymph_num>
    <bc_num>390</bc_num>     
    <mc_rate>0.033</mc_rate>
    <bc_rate>0.34</bc_rate>
    
    <phase>100</phase>	#分裂相，就是有效细胞数，一般每张图1-3个左右，标准按100采集
	<dic>2</dic>		#双着数，正常人0
	<trc>1</trc>		#三着数，正常人0
    <quc>0</quc>		#四着数，正常人0
    <pec>0</pec>		#五及更多着数，正常人0
    <f>1</f>			#长断片数，正常人0
    <min>0</min>		#微小体数，正常人0
    <r>0</r>			#着丝粒环数，正常人0
    <nr>0</nr>			#无着环，正常人0
    <abb_rate>0</abb_rate>	#畸变率，此项医生填写，0-1之间小数
    <marked_rate>0</marked_rate>#marked率，医生填写，0-1之间小数
  </calc>
  <diag>
	---
  </diag>
  <report>
    <date>20191209</date>
	<receiver></receiver>	# 接收者医生名，可空
	<receiver_time>2020-01-22 16:20</receiver_time>	#接收时间
	<inspecto></inspector>	#检查医生，可空
    <reviewer></reviewer>	#审核医生，可空
	<reviewer_time>2020-01-24 10:10</reviewer_time>	#审核时间
  </report>
</xml>
'''

def create_report():
    root = etree.Element('xml')
    return root

#baseinfo is a {} val,include all need items
def add_report_baseinfo(root,baseinfo):
    base_node = etree.SubElement(root, 'baseinfo')
    etree.SubElement(base_node, 'pname').text = baseinfo['pname'] #病人姓名
    etree.SubElement(base_node, 'pid').text = baseinfo['pid']   #病历号
    etree.SubElement(base_node, 'hid').text = baseinfo['hid']   #住院号
    etree.SubElement(base_node, 'bid').text = baseinfo['bid']   #病床号
    etree.SubElement(base_node, 'dept').text = baseinfo['dept'] #科别
    etree.SubElement(base_node, 'bar_code').text = baseinfo['bar_code']
    etree.SubElement(base_node, 'app_doctor').text = baseinfo['app_doctor'] #申请医生，可空
    etree.SubElement(base_node, 'app_time').text = baseinfo['app_time']     #申请时间 2020-01-22 15:30
    etree.SubElement(base_node, 'sampling_time').text = baseinfo['sampling_time'] #采样时间 2020-01-22 15:40
    etree.SubElement(base_node, 'test_item').text = baseinfo['test_item'] #标本类型
    etree.SubElement(base_node, 'age').text = baseinfo['age']
    etree.SubElement(base_node, 'sex').text = baseinfo['sex'] #性别 1：男， 0：女

def add_report_aerial(root):
    aerial = etree.SubElement(root, 'aerial_view')
    aerial.set('img', "aerial.jpg")

def add_report_mc(root):
    mc_node = etree.SubElement(root, 'mc')
    return mc_node

def add_report_mc_img(mc_node,imgname):
    etree.SubElement(mc_node, 'img').text = imgname

def add_report_calc(root,calcinfo):
    calc_node = etree.SubElement(root, 'calc')
    etree.SubElement(calc_node, 'images').text = calcinfo['images']
    etree.SubElement(calc_node, 'lymph').text  = calcinfo['lymph']
    etree.SubElement(calc_node, 'mc_cell').text= calcinfo['mc_cell']
    etree.SubElement(calc_node, 'mc').text     = calcinfo['mc']
    etree.SubElement(calc_node, 'bc').text     = calcinfo['bc']
    etree.SubElement(calc_node, 'mc_cell_rate').text = calcinfo['mc_cell_rate']
    etree.SubElement(calc_node, 'mc_rate').text= calcinfo['mc_rate']
    etree.SubElement(calc_node, 'bc_rate').text= calcinfo['bc_rate']

def add_report_diag(root):
    etree.SubElement(root, 'diag').text = ' '

# reportdate = 'yyyymmdd'
def add_report_reportinfo(root,reportinfo):
    report_node = etree.SubElement(root, 'report')
    etree.SubElement(report_node, 'reportdate').text = reportinfo['reportdate']  # 报告日期
    etree.SubElement(report_node, 'receiver').text = reportinfo['receiver'] # 接收者医生名
    etree.SubElement(report_node, 'receiver_time').text = reportinfo['receiver_time'] # 接收时间 2020-01-22 16:20
    etree.SubElement(report_node, 'inspector').text = reportinfo['inspector'] # 检查医生
    etree.SubElement(report_node, 'reviewer').text = reportinfo['reviewer'] # 审核医生
    etree.SubElement(report_node, 'reviewer_time').text = reportinfo['reviewer_time'] # 审核时间 2020-01-24 10:10


# ------------------------------------------------------------------------------
def write_pretty_xml(xmlname,root):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.ElementTree(root, parser=parser)
    tree.write(xmlname, xml_declaration=True,encoding='utf-8',pretty_print=True)
    #tree.write(xmlname, encoding="utf-8", xml_declaration=True)

if __name__ == '__main__':
    '''
    # roi.xml test
    rootxml = create_roi('my-patient-name')
    
    # one image
    imgnode = add_roi_imgname(rootxml,'0x1.jpg')
    
    # all boxes in one image
    myaxis = [100,120,500,600]
    add_roi_img_roi(imgnode,myaxis)
    
    myaxis = [101,121,501,601]
    add_roi_img_roi(imgnode,myaxis)

    write_pretty_xml('/dev/shm/rox.xml',rootxml)
    '''

    # report.xml
    report_root = create_report()

    baseinfo_node = {
        'pname':'new-one',
        'pid':'p0000',
        'hid':'n12345',     # Hospital number
        'dept':'体检中心',
        'bar_code':'bar-code',
        'test_item':'abberation',
        'age':'1',
        'sex':'1'
    }
    add_report_baseinfo(report_root,baseinfo_node)

    add_report_aerial(report_root)

    # mc and mc-images
    mc_ele = add_report_mc(report_root)
    add_report_mc_img(mc_ele,'123.jpg')
    add_report_mc_img(mc_ele,'456.jpg')

    # calc
    #calcinfo_node = {
    #    'mc_num':'100',
    #    'lymph_num':'10',
    #    'bc_num':'10',
    #    'mc_rate':'0.01',
    #    'bc_rate':'0.01'
    #}
    #add_report_calc(report_root,calcinfo_node)

    add_report_diag(report_root)

    #add_report_reportdate(report_root,'20200112')

    write_pretty_xml('/dev/shm/report.xml', report_root)
