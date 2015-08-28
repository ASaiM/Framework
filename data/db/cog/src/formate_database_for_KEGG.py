#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
from ftplib import FTP
import pickle
import inspect
import json_config_manipulation

###########
# Methods #
###########
def retrieve_gene_cog_mapping_seq_length(cog_info_filepath, seq_length_filepath, 
    gene_cog_mapping_filepath, protein_organism_mapping_filepath):
    cog_info_file = open(cog_info_filepath, 'r')
    
    cogs = {}
    gene_length_file = open(seq_length_filepath,'w')
    prot_organisms = {}
    Organisms_cogs = {}
    for line in cog_info_file.readlines():
        split_line = line[:-2].split(',')
        prot_id = split_line[2]
        organism = split_line[1]
        prot_length = split_line[3]
        cog_id = split_line[6]

        if not prot_organisms.has_key(prot_id):
            prot_organisms[prot_id] = organism
        elif prot_organisms[prot_id] != organism : 
            string = os.path.basename(__file__) + ' -- ' + inspect.stack()[1][3]
            string += ": " + prot_id 
            string += " already register with a different organism"
            raise ValueError(string)

        string = organism.lower() + ':' + prot_id + '\t' + prot_length + '\n'
        gene_length_file.write(string)

        cogs.setdefault(cog_id, []).append(organism + '#' + prot_id)

        Organisms_cogs.setdefault(organism, []).append(cog_id)
    gene_length_file.close()
    cog_info_file.close()

    gene_to_cog_file = open(gene_cog_mapping_filepath,'w')
    for cog in cogs:
        gene_to_cog_file.write(cog)
        for prot_id in cogs[cog]:
            gene_to_cog_file.write('\t' + prot_id.upper())
        gene_to_cog_file.write('\n') 
    gene_to_cog_file.close()

    protein_organism_mapping_file = open(protein_organism_mapping_filepath,'w')
    pickle.dump(prot_organisms,protein_organism_mapping_file)
    protein_organism_mapping_file.close()

    return Organisms_cogs

def retrieve_kegg_cog_mapping(filepath):
    kegg_cog_mapping_file = open(filepath,'r')
    kegg_cog_mapping_file_content = kegg_cog_mapping_file.readlines()
    kegg_cog_mapping_file.close()

    kegg_cog_mapping = {}
    for line in kegg_cog_mapping_file_content:
        split_line = line[:-1].split('\t')
        ko = split_line[0]
        cog = split_line[1:]

        kegg_cog = kegg_cog_mapping.setdefault(ko, [])
        kegg_cog += cog

    compt = 0
    for k in kegg_cog_mapping.keys():
        if len(kegg_cog_mapping[k]) > 1:
            compt += 1 
    print "\t\t", compt,"kegg categories with multiple cog"

    return kegg_cog_mapping

def test_kegg_presence(k, K_categories, kegg_cog_mapping, K_not_found):
    if k not in K_categories:
        K_categories.append(k)
    if not kegg_cog_mapping.has_key(k):
        if k not in K_not_found:
            K_not_found.append(k)
        return False
    else : 
        return True

def generation_cog_pathway_mapping(kegg_pathway_mapping_filepath, 
    cog_pathway_mapping_filepath, kegg_cog_mapping):
    kegg_pathway_mapping_file = open(kegg_pathway_mapping_filepath,'r')
    cog_pathway_mapping_file = open(cog_pathway_mapping_filepath,'w')
    cog_ko_mapping = {}
    for line in  kegg_pathway_mapping_file.readlines():
        split_line = line[:-1].split('\t')
        ko = split_line[0]
        ks = split_line[1:]
        module_string = ''
        for k in ks :
            if test_kegg_presence(k, K_categories,kegg_cog_mapping,K_not_found):
                module_string += '\t' + kegg_cog_mapping[k][0]
                for cog in kegg_cog_mapping[k]:
                    cog_ko_mapping.setdefault(cog, []).append(ko)
        if module_string != '':
            cog_pathway_mapping_file.write(ko + module_string + '\n')
    cog_pathway_mapping_file.close()
    kegg_pathway_mapping_file.close()
    return cog_ko_mapping

def transform_combination_from_kegg_to_cog(module):
    if isinstance(module,str):
        return ''
    if module._isleaf():
        k = module.m_pToken
        if test_kegg_presence(k, K_categories,kegg_cog_mapping,K_not_found):
            return kegg_cog_mapping[k][0]
        else : 
            return ''
    else :
        #s = '('
        s = ''
        module_str = str(module)
        for submodule in module.m_pToken:
            pos = module_str.find(str(submodule))
            #print module_str, module_str[pos-1]
            kegg_to_cog_str = transform_combination_from_kegg_to_cog(submodule)
            if kegg_to_cog_str != '':
                if s == '':
                    s += '('
                else :
                    s += module_str[pos-1]
                s += kegg_to_cog_str
        if s != '':
            s += ')'
        #print module, s
        return s

def generation_cog_module_mapping(input_dirpath, output_dirpath,
    kegg_cog_mapping):
    # modulec
    kegg_module_mapping_file = open(input_dirpath + '/modulec', 'r')
    module_mapping_file = open(output_dirpath + '/modulec','w')
    for line in kegg_module_mapping_file.readlines():
        split_line = line[:-1].split('\t')
        module = split_line[0]
        ks = split_line[1:]
        module_string = ''
        for k in ks :
            if test_kegg_presence(k, K_categories,kegg_cog_mapping,K_not_found):
                module_string += '\t' + kegg_cog_mapping[k][0]
        if module_string != '':
            module_mapping_file.write(module + module_string + '\n')
    module_mapping_file.close()
    kegg_module_mapping_file.close()

    # modulep
    kegg_module_mapping = pathway.open(open(input_dirpath + '/modulep'))
    module_mapping_file = open(output_dirpath + '/modulep','w')
    for module in kegg_module_mapping:
        module_id = module.m_strID
        module_detail = module.m_pPathway.m_pToken
        module_mapping_file.write(module_id)
        for submodule in module_detail:
            kegg_to_cog_str = transform_combination_from_kegg_to_cog(submodule)
            if kegg_to_cog_str != '':
                module_mapping_file.write('\t' + kegg_to_cog_str)
        module_mapping_file.write('\n')
    module_mapping_file.close()
    kegg_module_mapping_file.close()

def retrieve_organism_pathway(taxpc_filepath,Organisms_cogs,cog_ko_mapping):
    taxpc_file = open(taxpc_filepath,'w')
    for orga in Organisms_cogs.keys():
        ko_list = []
        for cog in Organisms_cogs[orga]:
            cog_ko = cog_ko_mapping.get(cog)
            if cog_ko != None :
           	    ko_list += cog_ko
        if ko_list != []:
            taxpc_file.write(orga)
            for ko in set(ko_list): #transforming into set to remove duplicates
           	    taxpc_file.write('\t' + ko + '#1')
            taxpc_file.write('\n')
    taxpc_file.close()

def complete_category_information(map_kegg_filepath, cogname_filepath, 
    map_cog_filepath):
    map_kegg_file = open(map_kegg_filepath,'r')
    map_kegg = {}
    for line in map_kegg_file.readlines():
        split_line = line[:-1].split('\t')
        detail = ' / '.join(split_line[1:])
        map_kegg.setdefault(split_line[0], detail)
    map_kegg_file.close()

    cog_detail_file = open(cogname_filepath,'r')
    for line in cog_detail_file.readlines()[1:]:
        split_line = line[:-1].split('\t')
        detail = ' / '.join(split_line[2:])
        map_kegg.setdefault(split_line[0], detail)
    cog_detail_file.close()

    map_kegg_file = open(map_cog_filepath,'w')
    for cat, detail in map_kegg.items():
        map_kegg_file.write(cat + "\t" + detail + "\n")
    map_kegg_file.close()

def extract_cog_module_pathway_mapping(input_filepath):
    if not os.path.exists(input_filepath):
        print "Directory content"
        print os.listdir(os.path.dirname(input_filepath))
        string = os.path.basename(__file__) + ": "
        string += input_filepath + " not found"
        raise ValueError(string)

        cog_module_pathway_mapping = {}
        cog_module_pathway_mapping_file = open(input_filepath, 'r')
        for line in cog_module_pathway_mapping_file.readlines():
            split_line = line[:-1].split('\t')
            module = split_line[0]
            module_list = cog_module_pathway_mapping.setdefault(module, []) 
            module_list += split_line[1:]
        cog_module_pathway_mapping_file.close()
        return cog_module_pathway_mapping

##############################################
# Formate cog database with kegg information #
##############################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw_data_dir', required=True)
    parser.add_argument('--extracted_data_dir', required=True)
    parser.add_argument('--kegg_formated_data_dir', required=True)
    parser.add_argument('--humann_dir', required=True)
    args = parser.parse_args()

    cog_dirpath = args.raw_data_dir
    cog_extracted_data_dirpath = args.extracted_data_dir
    kegg_formated_data_dirpath = args.kegg_formated_data_dir
    humann_dirpath = args.humann_dir
    kegg_info_dirpath = humann_dirpath + 'data/'

    if not os.path.exists(kegg_formated_data_dirpath):
        os.system('mkdir -p ' + kegg_formated_data_dirpath)

    command = 'cp ' + cog_extracted_data_dirpath + '/genels.gz ' 
    command += kegg_formated_data_dirpath
    os.system(command)
    command = 'cp ' + cog_extracted_data_dirpath + '/koc.gz ' 
    command += kegg_formated_data_dirpath
    os.system(command)
    
    # use HUMAnN code
    sys.path.append(humann_dirpath + 'src')
    import pathway

    # Formate cog data with kegg module/pathways
    #Organisms_cogs = retrieve_gene_cog_mapping_seq_length(cog_dirpath + "cog2003-2014.csv", cog_kegg_module_pathway_dir + 'genels', cog_kegg_module_pathway_dir + 'koc', cog_kegg_module_pathway_dir + 'protein_organism_mapping')
    kegg_cog_mapping = retrieve_kegg_cog_mapping(kegg_info_dirpath + 'cogc')

    K_not_found = []
    K_categories = []
    cog_ko_mapping = generation_cog_pathway_mapping(kegg_info_dirpath + '/keggc',
        kegg_formated_data_dirpath + 'keggc', kegg_cog_mapping)
    generation_cog_module_mapping(kegg_information_dirpath, 
        kegg_formated_data_dirpath,kegg_cog_mapping)

    K_not_found_file = open(kegg_formated_data_dirpath + '/kegg_not_found','w')
    for k in K_not_found:
        K_not_found_file.write(k + '\n')
    K_not_found_file.close())
    print "\t\t", len(K_not_found), "/", len(K_categories),
    print "kegg categories not found"

    retrieve_organism_pathway(kegg_formated_data_dirpath + 'taxpc', 
        Organisms_cogs,cog_ko_mapping)
    complete_category_information(kegg_information_dirpath + '/map_kegg.txt', 
        cog_dirpath + 'cognames2003-2014.tab', 
        kegg_formated_data_dirpath + 'map_kegg.txt')

    # Remove useless files
    os.system('rm -r ' + humann_dirpath)
    command = 'cp ' + kegg_formated_data_dirpath + '/* ' + kegg_info_dirpath
    os.system(command)
