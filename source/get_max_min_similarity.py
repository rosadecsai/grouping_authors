import pandas as pd
import numpy as np
import copy

def Read_Authors(name_file):
    f=open(name_file)
    lines = f.readlines()
    d_au=dict()
    for l in lines:
        #split -->
        aux = l.split(";")
        d_au.update({aux[0]:aux[1][:-1]})
    return d_au

def saveAut_Journal(rev_input,name_input,total):
    
    nf_out = "data_out/"+name_input+".csv"
    fout =open(nf_out,"wt")

    line=name_input+";Docs;%\n"
    fout.write(line)
    #get the list keys
    rev_keys=[*rev_input]
    min_n = len(rev_keys)
    for i in range(0,min_n):
        per=rev_input[rev_keys[i]]/total*100.0
        line=rev_keys[i]+";"+str(rev_input[rev_keys[i]])+";"+"{:.2f}".format(per)+"\n"
        fout.write(line)
    line="Total Papers;"+str(total)+";\n"
    fout.write(line)
    fout.close()

def create_info_author(aut_jour,name_input,name_max,name_min,code_input,code_max,code_min):
    #journals for the input author
    rev_input= aut_jour.loc[code_input,:]
    rev_input=dict({c:rev_input[c] for c in rev_input.index})
    rev_input={k: v for k, v in sorted(rev_input.items(), key=lambda item: item[1],reverse=True)}
    total_input=0
    for k in rev_input:
        total_input+=rev_input[k]
    #journals for the nearest author to the input author
    rev_max= aut_jour.loc[code_max,:]
    rev_max=dict({c:rev_max[c] for c in rev_max.index})
    rev_max={k: v for k, v in sorted(rev_max.items(), key=lambda item: item[1],reverse=True)}
    total_max=0
    for k in rev_max:
        total_max+=rev_max[k]
    #journals for the further author to the input author1
    rev_min= aut_jour.loc[code_min,:]
    rev_min=dict({c:rev_min[c] for c in rev_min.index})
    rev_min={k: v for k, v in sorted(rev_min.items(), key=lambda item: item[1],reverse=True)}
    total_min=0
    for k in rev_min:
        total_min+=rev_min[k]

    #erase from rev_min the journals which are not in rev_input
    kks=list(rev_min.keys())
    for k in kks:
        
        if (rev_input[k]==0 or rev_min[k]==0 ):
            del rev_min[k]
    #erase from rev_max the journals which are not in rev_input
    kks=list(rev_max.keys())
    for k in kks:
        if (rev_input[k]==0 or rev_max[k]==0 ):
            del rev_max[k]
    #erase from rev_input the journals which are not in rev_max OR in rev_min
    kks=list(rev_input.keys())
    for k in kks:
        if (rev_input[k]==0 or ((k not in rev_min) and (k not in rev_max))):
            del rev_input[k]

    saveAut_Journal(rev_input,name_input,total_input)
    saveAut_Journal(rev_max,name_max,total_max)
    saveAut_Journal(rev_min,name_min,total_min)
    
def main(name_input):
    names_files =["Author_Clus_1.txt","Author_Clus_2.txt","Author_Clus_3.txt","Author_Clus_4.txt"]
    d_autores_th=dict()
    for n in names_files:
        
        d=Read_Authors('data_out/'+n)
        print(d)
        d_autores_th.update(d)

    #search the input author
    code_input=""
    for k in d_autores_th.items():
        if (k[1]==name_input):
            code_input=k[0]
    print("Code ",code_input)
    #load the similarity
    similarity= pd.read_excel('data_out/similarity_core.xlsx',index_col=0)
    #drop the author that are not in d_autores_th
    cols=similarity.columns
    for c in cols:
        if (c not in d_autores_th):
            similarity=similarity.drop(c,axis=1)
            similarity=similarity.drop(c,axis=0)
    cols=similarity.columns
    #put auto-similarity to zero
    for c in cols:
        similarity.loc[c,c]=0

    max_similarity_author = similarity.columns[np.argmax(similarity.loc[code_input,:])]
    min_similarity_author=""
    th=0.6
    value_min = 1
    for c in cols:
        if ( code_input!=c and similarity.loc[code_input,c]>th and value_min >similarity.loc[code_input,c] ):
            min_similarity_author=c
            value_min=similarity.loc[code_input,c]
    #Read the author-journal frequency
    aut_jour= pd.read_excel("data_out/Corefrecuencias_author_journal_.xlsx",index_col=0)
    #number of commons journals
    
    commons_max=0
    commons_min=0
    n_input=0
    n_min=0
    n_max=0
    for c in aut_jour.columns:
        if aut_jour.loc[min_similarity_author,c]>0:
            n_min+=1
        if aut_jour.loc[max_similarity_author,c]>0:
            n_max+=1
        if aut_jour.loc[code_input,c]>0:
            n_input+=1
        if (aut_jour.loc[code_input,c]>0 and aut_jour.loc[min_similarity_author,c]>0 ):
            commons_min+=1
        if (aut_jour.loc[code_input,c]>0 and aut_jour.loc[max_similarity_author,c]>0 ):
            commons_max+=1
            


    aux_n="data_out/Relations_"+name_input+".txt"
    fout_Rel=open(aux_n,'wt')
    line="Number Journal where"+name_input+"has published "+str(n_input)+"\n"
    fout_Rel.write(line)
    line="Author more liked to "+name_input+ " "+d_autores_th[max_similarity_author]+" similarity "+str(similarity.loc[code_input,max_similarity_author])+" Commons_Journals "+str(commons_max)+"\n" 
    fout_Rel.write(line)
    line="\t\t Number Journal where he/she has published "+str(n_max)+"\n"
    fout_Rel.write(line)
    line="Author less liked to "+name_input+ " "+ d_autores_th[min_similarity_author]+" similarity "+str(value_min)+" Commons_Journals "+str(commons_min)+"\n" 
    fout_Rel.write(line)
    line="\t\t Number Journal where he/she has published "+str(n_min)+"\n"
    fout_Rel.write(line)
    fout_Rel.close()
    
    name_max = d_autores_th[max_similarity_author]
    name_min = d_autores_th[min_similarity_author]
    create_info_author(aut_jour,name_input,name_max,name_min,code_input,max_similarity_author,min_similarity_author)
    


    
    
    





if __name__ == "__main__":        
    #main("Bornmann, Lutz")  
    main("Batool, Syeda Hina")  

