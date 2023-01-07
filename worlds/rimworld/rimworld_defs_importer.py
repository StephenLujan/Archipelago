'''
This is a standalone tool to import data from a RimWorld installation
Assuming the output data is already present, archipelago need not run this.
'''
from typing import Dict, NamedTuple, Optional
import xml.etree.ElementTree as ET
import xmltodict
import pprint

RimWorldPath = 'F:\SteamLibrary\steamapps\common\RimWorld'
CorePath = RimWorldPath + '\Data\Core\Defs\ResearchProjectDefs'
BiotechPath = RimWorldPath + '\Data\Biotech\Defs\ResearchProjectDefs'
IdeologyPath = RimWorldPath + '\Data\Ideology\Defs\ResearchProjectDefs'
RoyaltyPath = RimWorldPath + '\Data\Royalty\Defs\ResearchProjectDefs'


def read_xml(path: str) -> dict:
    tree = ET.parse(path)
    xml_data = tree.getroot()
    xml_str = ET.tostring(xml_data, encoding='utf-8', method='xml')
    return dict(xmltodict.parse(xml_str))


def read_research_xml(path: str) -> list:
    return read_xml(path)['Defs']['ResearchProjectDef']


def process_parents(list: list[dict]):
    abstracts = {}
    # find abstracts
    for el in list:
        if '@Abstract' in el and el['@Abstract'] == 'True':
            abstracts[el['@Name']] = el

    # get list without abstracts
    list = [x for x in list if '@Abstract' not in x or x['@Abstract'] != 'True']

    # apply parents to abstracts to deal with nesting
    # (at least for a hierarchy 3 tall unless we repeat this)
    for k, v in abstracts.items():
        if '@ParentName' in v:
            parent = abstracts[v['@ParentName']]
            v.update({k: v for (k, v) in parent.items() if k[0] != '@'})

    # apply parents to non-abstract elements
    for el in list:
        if '@ParentName' in el:
            parent = abstracts[el['@ParentName']]
            el.update({k: v for (k, v) in parent.items() if k[0] != '@'})
            
    return list


item_id:int = 1000

item_id_to_defName:dict[int, str] = {}

item_id_to_label:dict[int, str] = {}

label_to_item_id:dict[str, int] = {}

pp = pprint.PrettyPrinter(width=79, compact=False, sort_dicts=False)

def add_numeric_ids(list: list[dict]):
    global item_id
    for research in list:
        try:
            item_id += 1
            item_id_to_defName[item_id] = research['defName']
            item_id_to_label[item_id] = research['label']
            label_to_item_id[research['label']] = item_id
        except BaseException as exception:
            pp.pprint(research)
            raise

def main():
    researches = {
        'research_1': read_research_xml(CorePath + '\ResearchProjects_1.xml'),
        'research_2': read_research_xml(CorePath + '\ResearchProjects_2_Electricity.xml'),
        'research_3': read_research_xml(CorePath + '\ResearchProjects_3_Microelectronics.xml'),
        'research_4': read_research_xml(CorePath + '\ResearchProjects_4_MultiAnalyzer.xml'),
        'research_5': read_research_xml(CorePath + '\ResearchProjects_5_Ship.xml'),
        'research_biotech_mech': read_research_xml(BiotechPath + '\ResearchProjects_Mechanitor.xml'),
        'research_biotech_misc': read_research_xml(BiotechPath + '\ResearchProjects_Misc.xml'),
        'research_ideology': read_research_xml(IdeologyPath + '\ResearchProjects_Misc.xml'),
        'research_royalty_apparel': read_research_xml(RoyaltyPath + '\ResearchProjects_Apparel.xml'),
        'research_royalty_implants': read_research_xml(RoyaltyPath + '\ResearchProjects_Implants.xml'),
        'research_royalty_music': read_research_xml(RoyaltyPath + '\ResearchProjects_MusicalInstruments.xml'),
    }


    def header(string:str)->str:
        '''create a more visible text header use in a python file'''
        return '\n' + '#' * 79 + '\n# ' + str.upper(string) + '\n' + '#' * 79 + '\n'

    with open('./data/research.py', 'w') as f:
        for key, value in researches.items():
            value = process_parents(value)
            f.write(header(key))
            f.write(key + ' = {}'.format(pp.pformat(value)))
            f.write('\n\n')
            add_numeric_ids(value)

    with open('./data/research_items.py', 'w') as f:
        f.write(header('id to defname'))
        f.write('item_id_to_defName = {}'.format(pp.pformat(item_id_to_defName)))
        f.write(header('id to label'))
        f.write('item_id_to_label = {}'.format(pp.pformat(item_id_to_label)))
        f.write(header('label to id'))
        f.write('label_to_item_id = {}'.format(pp.pformat(label_to_item_id)))




if __name__ == "__main__":
    main()
