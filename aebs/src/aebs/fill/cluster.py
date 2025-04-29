import numpy as np

from aebs.par import grouptypes

class aCluster:

  DX_LIMIT = 10.0
  DY_LIMIT = 2.0
  P_LIMIT = 14/255.0 # construction element probability threshold (see CVR3 source code)
  START_SLOPE = 0.0

  @classmethod
  def clusterGuardrail(cls, dxArray, dyArray, pArray, componentName, gtps, prj_name):
    arrayShape = dxArray.shape
    if len(arrayShape)!=2 or arrayShape!=dyArray.shape or arrayShape!=pArray.shape:
      raise ValueError('invalid input array shape!')
      
    if 'OHL' == componentName:
      CLUSTER_RANGE = grouptypes.OHL_GUARDRAILS
    elif 'FUS' == componentName:
      CLUSTER_RANGE = grouptypes.FUS_GUARDRAILS
    else:
      raise ValueError('invalid component name:' + componentName)
    CLUSTER_RANGE = [gtps.get_type(prj_name, type_name)
                     for type_name in sorted(CLUSTER_RANGE)]
    NOT_GUARDRAIL_CLUSTER = gtps.get_type(prj_name, 'NOT_GUARDRAIL')
    # NxM matrices in parameter
    N = arrayShape[0]
    M = arrayShape[1]
    
    # sort indices indirectly (according to dx distances)
    indicesSortedByDx = dxArray.argsort(axis=0)  # sort column-by-column (along 0th axis)
    rows, columns =  np.indices(dxArray.shape)
    
    # generate sorted arrays
    dxArraySorted = dxArray[indicesSortedByDx, columns]
    dyArraySorted = dyArray[indicesSortedByDx, columns]
    pArraySorted  = pArray[indicesSortedByDx, columns]
    
    # probability mask
    pMaskSorted = pArraySorted >= cls.P_LIMIT
    
    # array holding the clustering results
    clusterArray = np.ones(shape=dxArraySorted.shape, dtype='int16') * NOT_GUARDRAIL_CLUSTER
    
    # first cluster index
    firstCluster = CLUSTER_RANGE[0]
    
    # outer loop runs on time range (column-by-column)
    for j in xrange(M):
        clusterDict = {}  # mapping from clusterType to [lastElementIndex, lastSlope]
        
        if np.any(pMaskSorted[:,j]): # if there is construction element in the j. column
          firstIndex = np.where(pMaskSorted[:,j]==True)[0][0]  # save first construction element index (TODO: preprocess this step in 2D array)
          clusterDict[firstCluster] = (firstIndex, cls.START_SLOPE)
          clusterArray[firstIndex,j] = firstCluster
          
          # inner loop checks the objects at a fixed timestamp
          for i in xrange(firstIndex+1, N):
              if pMaskSorted[i,j]:  # next object is construction element
                clusterFound = False
                
                for clusterType, (lastElementIndex, lastSlope) in clusterDict.iteritems():
                    dxDiff = dxArraySorted[i,j] - dxArraySorted[lastElementIndex,j]
                    dyDiff = dyArraySorted[i,j] - dyArraySorted[lastElementIndex,j]
                    dyDiffEstimated = dxDiff*lastSlope

                    # put object into the current cluster if it fits
                    if (dxDiff > 1e-4) and (dxDiff < cls.DX_LIMIT) and (abs(dyDiffEstimated - dyDiff) < cls.DY_LIMIT):
                      clusterArray[i,j] = clusterType
                      clusterDict[clusterType] = (i, dyDiff/dxDiff)
                      clusterFound = True
                      break
                
                # assign new cluster to the object if it does not match to an existing cluster 
                if not clusterFound:
                  newClusterType = CLUSTER_RANGE[len(clusterDict)]
                  clusterDict[newClusterType] = (i, cls.START_SLOPE)
                  clusterArray[i,j] = newClusterType
        
        
    # # transforming the indices back
    # indicesSortedByDxInverse = indicesSortedByDx.argsort(axis=0)
    # return clusterArray[indicesSortedByDxInverse, columns]
    
    return (clusterArray, dxArraySorted, dyArraySorted, pArraySorted)
  
        
if __name__ == "__main__":
  from interface.grouptypes import GroupTypes

  prj_name = 'aebs'
  gtps = GroupTypes()
  gtps.add_types(prj_name, grouptypes.FUS_GUARDRAILS)
  gtps.add_types(prj_name, grouptypes.OHL_GUARDRAILS)
  gtps.add_types(prj_name, grouptypes.NOT_GUARDRAIL)
  gtps.prj_name = prj_name

  n = 40
  m = 5
  dxArray1 = (np.random.rand(n,m)*150).round(decimals=2) # dx in (0,150)
  dyArray1 = ( (np.random.rand(n,m)-0.5)*20 ).round(decimals=2) # dy in (-10,10)
  pArray1 = (np.random.rand(n,m)).round(decimals=2) # p in (0,1)
  
  clusterArray, dxArraySorted, dyArraySorted, pArraySorted = \
  aCluster.clusterGuardrail(dxArray1, dyArray1, pArray1, 'OHL', gtps)
  print clusterArray
  
  
