import os
from .parser import DFG_go, DFG_java, DFG_javascript, DFG_php, DFG_python, DFG_ruby
from .parser import (
    index_to_code_token,
    remove_comments_and_docstrings,
    tree_to_token_index,
)

from tree_sitter import Language, Parser
dfg_function={
    'python':DFG_python,
    'java':DFG_java,
    'ruby':DFG_ruby,
    'go':DFG_go,
    'php':DFG_php,
    'javascript':DFG_javascript
}

#load parsers
parsers={}        
for lang in dfg_function:
    dirname = os.path.dirname(__file__)
    LANGUAGE = Language('parser/my-languages.so', lang)
    parser = Parser()
    parser.set_language(LANGUAGE) 
    parser = [parser,dfg_function[lang]]    
    parsers[lang]= parser
    

def transform_raw_data_flow(idx_to_pos, d):
    dest = {'code': d[0], 'pos': idx_to_pos[d[1]]}
    srcs = [{'code': code, 'pos': idx_to_pos[idx]} for code, idx in zip(d[3], d[4])]
    return (dest, d[2], srcs)

    
#remove comments, tokenize code and extract dataflow                                        
def extract_dataflow(code, lang):
    parser = parsers[lang]
    #obtain dataflow
    # try:
    #     code = remove_comments_and_docstrings(code, lang)
    # except:
    #     pass
    if lang=="php":
        code="<?php"+code+"?>"    
    code_bytes = bytes(code, 'utf8')
    try:
        tree = parser[0].parse(code_bytes)    
        root_node = tree.root_node  
        tokens_index=tree_to_token_index(root_node)     
        code=[bytes(line, 'utf8') for line in code.split('\n')]
        code_tokens=[index_to_code_token(x,code) for x in tokens_index]  
        index_to_code={}
        # index: (start_point, end_point)
        # idx: index of token in code_tokens
        for idx,(index,code) in enumerate(zip(tokens_index,code_tokens)):
            index_to_code[index]=(idx,code)
        idx_to_pos={} # pos: start_point, i.e. (line_no - 1, col_offset) (here col_offset is UTF-8 byte offset!)
        for index in index_to_code:
            idx, code = index_to_code[index]
            idx_to_pos[idx] = index[0]
        # print('code_tokens', code_tokens)
        # print('index_to_code', index_to_code)
        # print('idx_to_pos', idx_to_pos)
        try:
            DFG,_=parser[1](root_node,index_to_code,{}) 
        except:
            DFG=[]
        DFG=sorted(DFG,key=lambda x:x[1])
        indexs=set()
        for d in DFG:
            if len(d[-1])!=0:
                indexs.add(d[1])
            for x in d[-1]:
                indexs.add(x)
        new_DFG=[]
        for d in DFG:
            if d[1] in indexs and len(d[-1]) != 0:
                new_DFG.append(transform_raw_data_flow(idx_to_pos, d))
        dfg=new_DFG
    except:
        code_tokens = []
        dfg=[]
    # print(dfg)
    return dfg
