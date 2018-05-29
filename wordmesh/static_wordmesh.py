#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 27 02:20:39 2018

@author: mukund
"""
import gensim
from utils import cooccurence_similarity_matrix as csm
import numpy as np
from sklearn.manifold import MDS
from utils import _save_wordmesh_as_html, _get_bb_dimensions
from force_directed_model import equilibrium_positions

class StaticWordmesh():
    def __init__(self, text, dimensions=(100, 100),
                 keyword_extractor='textrank', lemmatize=True,
                 pos_filter=('NN', 'JJ', 'RB', 'VB')):
             
        """Word mesh object for generating and drawing STATIC 
        wordmeshes/wordclouds.
        
        Parameters
        ----------
        text : string
            The string of text that needs to be summarized
            
        dimensions : tuple, optional 
            The desired dimensions (height, width) of the wordcloud in pixels
            
        keyword_extractor : string, optional
            You can choose one from the following: ['textrank']
            
        lemmatize : bool, optional
            Whether the text needs to be lemmatized before keywords are
            extracted from it
            
        pos_filter : tuple, optional
            A POS filter can be applied on the keywords. By default, only nouns,
            adjectives, adverbs and verbs can be keywords.
            More more information on the tags used, visit:
            https://www.clips.uantwerpen.be/pages/mbsp-tags
            
        Returns
        -------
        StaticWordMesh
            A word mesh object 
        
        """
        
        self.text = text
        self.extractor = keyword_extractor
        self.dimension_ratio = dimensions[0]/float(dimensions[1])
        self.resolution = dimensions
        self.lemmatize = True
        self.keyword_extractor = keyword_extractor
        self.pos_filter = pos_filter
        self._extract_keywords()
        self.set_fontsize()
        self.set_fontcolor()
        self.set_clustering_criteria()

    def _extract_keywords(self):
        self.keywords = []
        scores = []
        word_scores = None
        
        
        if self.keyword_extractor == 'textrank':
            word_scores = gensim.summarization.keywords(self.text, split=True, 
                                                    scores=True, 
                                                    lemmatize=self.lemmatize,
                                                    pos_filter=self.pos_filter)
        else:
            raise NotImplementedError("Only 'textrank' has been implemented")
            
        for word_score in word_scores:
            self.keywords.append(word_score[0])
            scores.append(word_score[1])
        
        self.scores = np.array(scores)

    def set_fontsize(self, by='scores', custom_sizes=None, 
                     directly_proportional=True):
        """
        This function can be used to pick a metric which decides the font size
        for each extracted keyword. By default, the font size is directly 
        proportional to the 'scores' assigned by the keyword extractor. 
        
        Fonts can be picked by: 'scores', 'word_frequency', 'random', None
        
        You can also choose custom font sizes by passing in a dictionary 
        of word:fontsize pairs using the argument custom_sizes
        
        Parameters
        ----------
        
        by : string or None, optional
            The metric used to assign font sizes. Can be None if custom sizes 
            are being used
        custom_sizes : dictionary or None, optional
            A dictionary with individual keywords as keys and font sizes as
            values. The dictionary should contain all extracted keywords (that 
            can be accessed through the keywords attribute). Extra words will
            be ignored
        directly_proportional : bool, optional
            Controls whether font sizes are directly or inversely proportional
            to the value of the chosen metric
            
        Returns
        -------
        
        numpy array
            Array of normalized font sizes, normalized such that the maximum 
            is 1. There is a one-one correspondence between these and the 
            extracted keywords
        """
        
        if by=='scores' and directly_proportional:
            self.fontsizes_norm = self.scores/self.scores.max()
            
        else:
            raise NotImplementedError()
            
        return self.fontsizes_norm
            
    def set_fontcolor(self, by='random', custom_colors=None):
        """
        This function can be used to pick a metric which decides the font color
        for each extracted keyword. By default, the font size is assigned 
        randomly 
        
        Fonts can be picked by: 'random', 'word_frequency', None
        
        You can also choose custom font colors by passing in a dictionary 
        of word:fontcolor pairs using the argument custom_sizes, where 
        fontcolor is an (R, G, B) tuple
        
        Parameters
        ----------
        
        by : string or None, optional
            The metric used to assign font sizes. Can be None if custom colors 
            are being used
        custom_colors : dictionary or None, optional
            A dictionary with individual keywords as keys and font colors as
            values (these should be RGB tuples). The dictionary should contain
            all extracted keywords (that can be accessed through the keywords 
            attribute). Extra words will be ignored
            
        Returns
        -------
        
        numpy array
            A numpy array of shape (num_keywords, 3).
        """
        
        if by=='random':
            rnd = lambda x: int(np.random.randint(0, 140))
            colors = [(230, 110+rnd(0),
                       110+rnd(0)) for i in range(len(self.keywords))]
            self.fontcolors = np.array(colors)
            
        else:
            raise NotImplementedError()
            
        return self.fontcolors
            
    def set_clustering_criteria(self, by='cooccurence', 
                          custom_similarity_matrix=None):
        """
        This function can be used to define the criteria for clustering of
        different keywords in the wordcloud. By default, clustering is done
        based on the tendency of words to frequently occur together in the
        text i.e. the 'cooccurence' criteria is used for clustering
        
        The following pre-defined criteria can be used: 'cooccurence',
        'semantic_similarity', 'pos_tag'
        
        You can also define a custom criteria
        
        Parameters
        ----------
        
        by : string or None, optional
            The pre-defined criteria used to cluster keywords
            
        custom_similarity_matrix : numpy array or None, optional
            A 2-dimensional array with shape (num_keywords, num_keywords)
            The entry a[i,j] defines the similarity between keyword[i] and 
            keyword[j]. Words that are similar will be clustered together
            
        Returns
        -------
        
        numpy array
            the similarity_matrix, i.e., a numpy array of shape (num_keywords, 
            num_keywords).
        """
        if by=='cooccurence':
            self.similarity_matrix = csm(self.text, self.keywords)
            
        else:
            raise NotImplementedError()
            
        self._generate_embeddings()
        return self.similarity_matrix
    
    
    def _generate_embeddings(self):
        mds = MDS(2, dissimilarity='precomputed').\
                             fit_transform(self.similarity_matrix)
        bbd = _get_bb_dimensions(self.keywords, self.fontsizes_norm*100)
        
        self.embeddings = equilibrium_positions(mds, bbd)

    def save_as_html(self, force_directed_animation=False):
        """
        Temporary
        """  
        _save_wordmesh_as_html(self.embeddings, self.keywords, 
                               self.fontsizes_norm*100, True)