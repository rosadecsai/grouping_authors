## The grouping of scholars who belong to the same invisible college using journal coupling


### Dataset
The dataset can be downloaded from [here](https://drive.ugr.es/index.php/s/I8BKFvpVQtVdYZ5). The dataset was built in May 2024. We collected the information of every author from Web of Science.

### Source
* search_similarity_author_journal generates different files. Between them, we note:
  *  similarity_core.csv and similarity_core.net: Contain the similarity matrix between different authors. With  similarity_core.net, you can use [Pajek software](http://mrvar.fdv.uni-lj.si/pajek/).
  *  Show the dendrogram image. For every cluster, create two sets of files Author_ClusAll_<n>.txt, which stores the author within the cluster. Also, it creates the clus_<n>.txt with the journal and weight by cluster
*  get_max_min_similarity gets the more and less similar author to an input author.

García, J.A (jags@decsai.ugr.es), Rodriguez-Sanchez, Rosa (rosa@decsai.ugr.es) and Fdez-Valdivia, J (jfv@decssai.ugr.es) 
University of Granada
  
