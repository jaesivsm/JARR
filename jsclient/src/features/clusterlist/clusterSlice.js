import axios from 'axios';
import qs from 'qs';
import { createSlice } from '@reduxjs/toolkit';
import { apiUrl } from '../../const.js';

const clusterSlice = createSlice({
  name: 'cluster',
  initialState: { filters: {},
                  loading: false,
                  clusters: [],
  },
  reducers: {
    askedClusters(state, action) {
      return { ...state, filters: action.payload.filters, loading: true };
    },
    loadedClusters(state, action) {
      return { ...state, loading: false,
               clusters: action.payload.clusters };
    },
  },
});

export const { askedClusters, loadedClusters } = clusterSlice.actions;
export default clusterSlice.reducer;

export const doFetchClusters = (
  filters: object,
): AppThunk => async (dispatch, getState) => {
  dispatch(askedClusters(filters));
  const params = qs.stringify(getState().clusters.filters);
  const result = await axios({
    method: 'get',
    url: apiUrl + '/clusters?' + params,
    headers: { 'Authorization': getState().login.token },
  });
  dispatch(loadedClusters({ clusters: result.data }))
}
