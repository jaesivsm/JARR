import axios from 'axios';
import qs from 'qs';
import { createSlice } from '@reduxjs/toolkit';
import { apiUrl } from '../../const.js';

const clusterSlice = createSlice({
  name: 'cluster',
  initialState: { filters: {},
                  loadingClusterList: false,
                  loadingCluster: false,
                  clusters: [],
                  selected: {},
                  requestedClusterId: null,
                  loadedCluster: {},
  },
  reducers: {
    requestedClustersList(state, action) {
      const selected = {};
      const filters = {};
      if (!!action.payload.filters.feedId) {
        selected.feedId = filters.feed_id = action.payload.filters.feedId;

      } else if (!!action.payload.filters.categoryId) {
        selected.categoryId = filters.category_id = action.payload.filters.categoryId;
      }

      return { ...state, filters, selected, loadingClusterList: true };
    },
    retrievedClustersList(state, action) {
      return { ...state, loadingClusterList: false,
               clusters: action.payload.clusters };
    },
    requestedCluster(state, action) {
      return { ...state, loadingCluster: true,
               requestedClusterId: action.payload.clusterId,
      };
    },
    retrievedCluster(state, action) {
        // TODO remove old cluster
      return { ...state, loadingCluster: false,
               loadedCluster: action.payload.cluster,
      };
    },
  },
});

export const { requestedClustersList, retrievedClustersList,
               requestedCluster, retrievedCluster,
} = clusterSlice.actions;
export default clusterSlice.reducer;

export const doListClusters = (
  filters: object,
): AppThunk => async (dispatch, getState) => {
  dispatch(requestedClustersList({ filters: filters }));
  const params = qs.stringify(getState().clusters.filters);
  const result = await axios({
    method: 'get',
    url: apiUrl + '/clusters?' + params,
    headers: { 'Authorization': getState().login.token },
  });
  dispatch(retrievedClustersList({ clusters: result.data }))
}

export const doReadCluster = (clusterId: number): AppThunk => async (dispatch, getState) => {
  dispatch(requestedCluster({ clusterId }));
  const result = await axios({
    method: 'get',
    url: apiUrl + '/cluster/' + clusterId,
    headers: { 'Authorization': getState().login.token },
  });
  dispatch(retrievedCluster({ cluster: result.data }))
}
