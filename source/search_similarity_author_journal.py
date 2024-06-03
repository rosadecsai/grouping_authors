import numpy as np
import pandas as pd
import math

from scipy.cluster.hierarchy import linkage, dendrogram, fcluster,set_link_color_palette
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity

def createDendogramCluster( similarity,name_out_cluster,dataAuthors,numclust=5,th=0.6,prune=False,showplot=False):
    aux=similarity.copy()
    plt.figure(figsize=(12,20))
    dissimilarity = 1.0 - (aux.values)
   
    Z = linkage((dissimilarity), 'complete')
    if showplot==True:
        set_link_color_palette(['y','g', 'r','b'])
        dendrogram(Z, labels=similarity.columns, orientation='right')
        plt.show()
    
    fl = fcluster(Z,numclust,criterion='maxclust')
    #Write to .clu to read in pajek
    f=open(name_out_cluster,'wt')
    line ="*Vertices "+str(len(fl))+"\n"
    f.write(line)
    for i in fl:
        line=str(i)+"\n"
        f.write(line)
    
    f.close()
    stay=1-np.zeros(len(similarity.columns))
    if prune:
        
        aux = similarity.copy()
        for i in range(0,len(aux.columns)):
            any=False
            for j in range(0,len(aux.columns)):
                if(aux.values[i,j]<th):
                    aux.values[i,j]=0
                elif i!=j and any==False:
                    any=True
            if (any==False):
                stay[i]=0
    d = dict({i+1:[] for i in range(0,numclust)})

    for i in range(0,len(similarity.columns)):
        if (stay[i]==1):
            #add the author and the info associated Name and Affiliation
            d[fl[i]].append((similarity.columns[i],dataAuthors[similarity.columns[i]]))
    return d        

def read_file(name_file):
    with open(name_file) as f: 
        lines = f.readlines() 
        d=dict()
        
        for l in lines:
            l=l[:-1]
            aux = l.split(';')
            if (len(aux)>1):
                print(aux)
                afil=[ k for k in aux[4:]]
                #d.update({aux[1]:aux[0]})
                if aux[1] not in d:
                    d[aux[1]]={'Name':aux[0],'Afil':afil}
            
            
        return d
    return {}
            
def get_journals(autores_core,path):
    journals =set()
    
    
    for a in autores_core.items():
        #open the excel
        file_ex =path+a[0]+".xls"
        data_author = pd.read_excel(file_ex)
        for s in data_author.index:
            name_jour = data_author.loc[s,'Journal Abbreviation']
            if not (not name_jour or pd.isnull(name_jour)):
                journals.add(name_jour)
    #journals.discard(np.nan)
    return journals;          
      
def get_journal_one_author(autor_input,path): 
    journals =set()
    file_ex =path+autor_input[0]+".xls"
    data_author = pd.read_excel(file_ex)
    for s in data_author.index:
        name_jour = data_author.loc[s,'Journal Abbreviation']
        if not (not name_jour or pd.isnull(name_jour)):
            journals.add(name_jour)
    #journals.discard(np.nan)
    return journals


def join_journals(jour1,jour2):
    journals =jour1.copy()
    journals.update(jour2)
    return journals



def save_to_pajekWholeGraph(data,name_out,author_core=None):
    total_vertices = len(data.index)
    
    index = data.index
    nfilas = len(index)
    ncols = nfilas
    
    with open(name_out,'wt') as fout:
        line= "*Vertices\t"+str(total_vertices)+'\n'
        fout.write(line)
        #write the input author
       
        
        for k in range(0,nfilas):
            xfact=1.5
            yfact=1.5
            color="CadetBlue"
            bc="Black"
            label_vert=index[k]
            if author_core!=None:
                label_vert = author_core[index[k]]['Name']

            line=str(k+1)+"\t\""+label_vert+"\""+ " x_fact "+str(xfact)+" y_fact "+str(yfact)+" ic "+ color+ " bc "+bc+" fos 20 \n"
            fout.write(line)
         
        line="*Edges\n"
        fout.write(line)
        mat = data.values;
        
        for r in range(0,nfilas):
            for c in range(0,ncols):
                if (mat[r,c]!=0 and r!=c ):
                    line = str(r+1)+" "+str(c+1)+" "+str(mat[r,c])+" c Gray25\n"
                    fout.write(line)

        

def save_to_pajek(data,name_out,th=0.01,top=None,ifbet_rev=True):
    if top!=None:
        name_out = name_out+"th_"+str(th)+"_top"+str(top)+".net"
        total_vertices = top+1
    else:
        name_out = name_out+"th_"+str(th)+".net"
        total_vertices = len(data.index)
    
    index = data.index
    
    
    nfilas = len(index)
    ncols = nfilas
    #select vertices connect to input author (51) and connect value is bigger than th
    #top=10 #limited to top-reviewers
    select_reviewer =dict()
    
    nselect=0
    pos_ref=nfilas-1
    for i in range(0,len(index)-1):
        if data.values[i,pos_ref]>th:
            select_reviewer.update({index[i]: {'simi':data.values[i,pos_ref],'pos':i} })
            
            nselect+=1
            if (top!=None and nselect==top):
                break
    
    #sort select_reviewer by simi
    select_reviewer=dict(sorted(select_reviewer.items(), key=lambda x:x[1]['simi'],reverse=True))
    
    i=1
    ind_vert={}
    with open(name_out,'wt') as fout:
        line= "*Vertices\t"+str(total_vertices)+'\n'
        fout.write(line)
        #write the input author
        xfact=3
        yfact=3
        color="Red"
        bc="BrickRed"
        ind_vert.update({index[nfilas-1]:i})
        line=str(i)+"\t\""+index[nfilas-1]+"\""+ " x_fact "+str(xfact)+" y_fact "+str(yfact)+" ic "+ color+ " bc "+bc+" fos 20 \n"
        fout.write(line)
        
        for k in select_reviewer.items():
            xfact=1.5
            yfact=1.5
            color="CadetBlue"
            bc="Black"
            i+=1
            ind_vert.update({k[0]:i})
            line=str(i)+"\t\""+k[0]+"\""+ " x_fact "+str(xfact)+" y_fact "+str(yfact)+" ic "+ color+ " bc "+bc+" fos 20 \n"
            fout.write(line)
        
        line="*Edges\n"
        fout.write(line)
        mat = data.values;
        #max_v = np.max(mat[nfilas-1,:])
        r=nfilas-1
        pos_gr1=ind_vert[index[nfilas-1]]
        for k in select_reviewer.items():
            
            c= k[1]['pos']
            v = mat[r,c]
            pos_gr2= ind_vert[k[0]]
            if (mat[r,c]!=0 and r!=c ):
                line = str(pos_gr1)+" "+str(pos_gr2)+" "+str(v)+" c Gray25\n"
                fout.write(line)

        if (ifbet_rev==True):
            for k1 in select_reviewer.items():
                pos_gr1= ind_vert[k1[0]]
                r= k1[1]['pos']    
                for k2 in select_reviewer.items():
                    c= k2[1]['pos']
                    v = mat[r,c]
                    pos_gr2= ind_vert[k2[0]]
                    if (mat[r,c]!=0 and r!=c ):
                        line = str(pos_gr1)+" "+str(pos_gr2)+" "+str(v)+" c Gray25\n"
                        fout.write(line)

    return select_reviewer            






def create_matrix (autores_core,author_input,path_input,path_output):
    journals_core = get_journals(autores_core,path_input)
    print("Journal core ",len(journals_core))
    print("Revistas",journals_core)
    journals_author = get_journal_one_author(author_input,path_input)
    print("Journal input",len(journals_author))
    print("Revistas",journals_author)
    
    journals = join_journals(journals_core,journals_author)
    print("Journals union ",len(journals))
    aut_jou= pd.DataFrame(0,index=list(autores_core.keys())+[author_input[0]],columns=list(journals))
    for a in autores_core.items():
        #open the excel
        file_ex =path_input+a[0]+".xls"
        data_author = pd.read_excel(file_ex)
        for s in data_author.index:
            name_jour = data_author.loc[s,'Journal Abbreviation']
            if not (not name_jour or pd.isnull(name_jour)):
                aut_jou.loc[a[0],data_author.loc[s,'Journal Abbreviation']]+=1
    file_ex =path_input+author_input[0]+".xls"
    data_author = pd.read_excel(file_ex)
    for s in data_author.index:
            name_jour = data_author.loc[s,'Journal Abbreviation']
            if not (not name_jour or pd.isnull(name_jour)):
                aut_jou.loc[author_input[0],data_author.loc[s,'Journal Abbreviation']]+=1

    name_output=path_output+"frecuencias_author_journal_"+author_input[0]+".xlsx"
    aut_jou.to_excel(name_output,index=True)
    return aut_jou





def create_matrixOnlyCore (autores_core,path_input,path_output):
    journals = get_journals(autores_core,path_input)
    print("Journal core ",len(journals))
    print("Revistas",journals)
    
    print("#Journals  ",len(journals))
    aut_jou= pd.DataFrame(0,index=list(autores_core.keys()),columns=list(journals))
    
    for a in autores_core.items():
        #open the excel
        file_ex =path_input+a[0]+".xls"
        data_author = pd.read_excel(file_ex)
        for s in data_author.index:
            name_jour = data_author.loc[s,'Journal Abbreviation']
            if not (not name_jour or pd.isnull(name_jour)):
                aut_jou.loc[a[0],data_author.loc[s,'Journal Abbreviation']]+=1
        
    name_output=path_output+"Corefrecuencias_author_journal_"+".xlsx"
    aut_jou.to_excel(name_output,index=True)
    return aut_jou


def get_B(data,name_output,ifsel_rev=False,):
    #get td-idf between author and journal
    N= len(data.index)
    print("N ",N)
    mat_w=data.copy()
    
    for j in data.columns:
        n_m=0
        for l in data.index:
            if data.loc[l,j]>0:
                n_m+=1
        factor=0
        if (n_m!=0):
            factor = math.log(N/n_m)
        for i in data.index:
            mat_w.loc[i,j]=data.loc[i,j]*factor

    
    #get cosine similarity of order first
    B=cosine_similarity(mat_w.values)
    
    #get cosine similarity of order second
    S=cosine_similarity(B)
  
    
    #create a dataframe
    similarity=pd.DataFrame(S,index=data.index,columns=data.index)
    similarity.to_excel(name_output+".xlsx")
     
    if ifsel_rev:
        select_reviewer=save_to_pajek(similarity,name_output,top=10)
        return select_reviewer
    else:
        return similarity

def AreCoauthors(id1,id2,path_input):
    print("Id1 ",id1," ID2 ", id2)
    file_ex =path_input+id1+".xls"
    data_id1 = pd.read_excel(file_ex)
    file_ex =path_input+id2+".xls"
    data_id2 = pd.read_excel(file_ex)
    dois_id1=set()
    
    for s in data_id1.index:
        name_jour = data_id1.loc[s,'Journal Abbreviation']
        if not (not name_jour or pd.isnull(name_jour)):
            dois_id1.add(data_id1.loc[s,'DOI'])
    for s in data_id2.index:
        name_jour = data_id2.loc[s,'Journal Abbreviation']
        if not (not name_jour or pd.isnull(name_jour)):
            if not (not data_id2.loc[s,'DOI'] or pd.isnull(data_id2.loc[s,'DOI'])) and data_id2.loc[s,'DOI'] in dois_id1:
                
                return True
        

    return False            
            


            
def SameAfil(r1,r2):
    for af1 in r1['Afil']:
        for af2 in r2['Afil']:
            if (af1==af2):
                return True
    return False


def main_withinput(file_core,file_test,path_input,path_output):
    fileauthor_core = file_core
    fileauthor_test = file_test
    author_core=read_file (fileauthor_core)
    author_test=read_file (fileauthor_test)
    print(author_core)

    print("___________")
    print(author_test)
    for a in author_test.items():
        aut_jou=create_matrix(author_core,a,path_input,path_output)
        name_out = path_output+"similarity_"+a[0]
        reviewer_select = get_B(aut_jou,name_out,True)
        list_reviewer = [k[0] for k in reviewer_select.items()]
        print("Revisores potenciales ",len(list_reviewer))
        nn_input_ref=path_output+a[0]+"__besttres.txt"
        
        f2=open(nn_input_ref,'wt')
        
        #list_reviewer.append(a[0])
        n_reviewers=0
        for rev in list_reviewer:
            if SameAfil(author_core[rev],author_test[a[0]])==False and  AreCoauthors(rev,a[0],path_input)==False:
                f2.write('______________________________\n')
                f2.write(rev+" "+"Simi: "+str(reviewer_select[rev]['simi'])+"\n")
                str_afil = ";".join(author_core[rev]['Afil'])
                f2.write("Afil:"+str_afil+'\n')
                total_rev = aut_jou.loc[rev,:].sum()
                f2.write("Total Docs:"+str(total_rev)+'\n')
                for c in aut_jou.columns:
                    if (aut_jou.loc[rev,c]>0 and aut_jou.loc[a[0],c]>0):
                        manus_journal = aut_jou.loc[rev,c]
                        perce = aut_jou.loc[rev,c]/total_rev*100.0
                        f2.write(c+"\t"+str(manus_journal)+"\t"+str(perce)+"\n")
                f2.write("\n\n");
                #n_reviewers+=1
                #if (n_reviewers==3):
                #-------------------------------------    break;
        f2.write('INPUT AUTHOR ______________________________\n')
        f2.write(a[0]+'\n')
        str_afil = ";".join(author_test[a[0]]['Afil'])
        f2.write('Afil:'+str_afil+'\n')
        
        total_rev = aut_jou.loc[a[0],:].sum()
        f2.write("Total Docs:"+str(total_rev)+'\n')
        for c in aut_jou.columns:
            if aut_jou.loc[a[0],c]>0:
                manus_journal = aut_jou.loc[a[0],c]
                perce = aut_jou.loc[a[0],c]/total_rev*100.0
                f2.write(c+"\t"+str(manus_journal)+"\t"+str(perce)+"\n")
                
        f2.close()




        break;


    
def main_onlycore(file_core,path_input,path_output):
    fileauthor_core = file_core
    
    author_core=read_file (fileauthor_core)
    for i,a in enumerate(author_core.items()):
        print(i," ", a[0]," ",a[1]['Name'])
    print("___________")
    
    print("Lineas leidas ",len(author_core))
    aut_jou=create_matrixOnlyCore(author_core,path_input,path_output)
    name_out = path_output+"similarity_core"
    similarity= get_B(aut_jou,name_out)
    save_to_pajekWholeGraph(similarity,name_out+".net",author_core)
    nclust=4
    dclusters=createDendogramCluster(similarity,"data_out/clusters.clu",author_core,numclust=nclust,th=0.6,prune=True,showplot=True)
    #create a dataframe rows clusters columns journals
    m=np.zeros((nclust,len(aut_jou.columns)))
    clus_jour= pd.DataFrame(m,index=np.arange(1,nclust+1),columns=aut_jou.columns)
    
    
    for k in dclusters:#for each cluster
        name_f = 'data_out/Author_Clus_'+str(k)+'.txt'
        file_c=open(name_f,'wt')
        print("Cluster ",k)
        for p in dclusters[k]: #for each author in the cluster k
            print(p[0],"-->",p[1]['Name'])
            line =str(p[0])+';'+p[1]['Name']+'\n'
            file_c.write(line)
            #loop over the journals for author p[0]
            for j in aut_jou.columns:
                #increase in cluster k the amount of publishing by the author p[0]
                clus_jour.loc[k,j]+=aut_jou.loc[p[0],j]
        file_c.close()     

    clus_jour.to_excel('data_out/clust_jour_fre.xlsx')
    print(clus_jour.columns)
    #create the tdidf by cluster

    m= np.zeros((nclust,len(clus_jour.columns)),dtype=np.float32)
    mat_w=pd.DataFrame(m,index=clus_jour.index,columns=clus_jour.columns)
    fall_jour=open("data_out/Journal_inAllCluster.txt",'wt')
    line ="Journal;Frequency\n"
    for j in clus_jour.columns:
        n_m=0
        for l in clus_jour.index:
            if clus_jour.loc[l,j]>0:
                n_m+=1
        if (n_m==nclust):
            line = j+";"
            for l in clus_jour.index:
                line+=str(clus_jour.loc[l,j])+";"
            line=line[:-1]
            line+="\n"   

            fall_jour.write(line)

        factor=0
        if (n_m!=0):
            factor = math.log(nclust/n_m)
        for i in clus_jour.index:
            mat_w.loc[i,j]=clus_jour.loc[i,j]*factor
    fall_jour.close()            
    print(mat_w.head())
    for c in mat_w.index:
        nfile_cls="data_out/clust_"+str(c)+'.txt'
        f=open(nfile_cls,'wt')
        ind_jour = np.argsort(mat_w.loc[c,:])
        ind_jour=np.flip(ind_jour)
        pos=1
        for j in range(0,len(mat_w.columns)):
            line = str(pos)+";"+mat_w.columns[ind_jour[j]]+";"+str(mat_w.loc[c,mat_w.columns[ind_jour[j]]])+'\n'
            f.write(line)
            pos+=1
    

  







if __name__ == "__main__":
    #CODIGO CUANDO TIENES CORE y UN TEST
    #p_data ="data/"
    #file_core = p_data+'autores_doi.txt'
    #file_test = p_data+'autores_test.txt'
    #main_withinput(file_core,file_test,p_data,'data_out/')        

    #Only Core
    path_input ="data/"
    path_output="data_out/"
    file_core = path_input+'autores_doi.txt'
    main_onlycore(file_core,path_input,path_output)
