import axios from 'axios';
import qs from 'qs';
import { createSlice } from '@reduxjs/toolkit';
import { apiUrl } from '../../const.js';

const clusterSlice = createSlice({
  name: 'cluster',
  initialState: { filters: {},
                  loading: false,
                  clusters: [],
                  selected: {},
  },
  reducers: {
    askedClusters(state, action) {
      const selected = {};
      const filters = {};
      if (!!action.payload.filters.feedId) {
        selected.feedId = filters.feed_id = action.payload.filters.feedId;

      } else if (!!action.payload.filters.categoryId) {
        selected.categoryId = filters.category_id = action.payload.filters.categoryId;
      }

      return { ...state, filters, selected, loading: true };
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
  dispatch(askedClusters({ filters: filters }));
  const params = qs.stringify(getState().clusters.filters);
  const result = await axios({
    method: 'get',
    url: apiUrl + '/clusters?' + params,
    headers: { 'Authorization': getState().login.token },
  });
  dispatch(loadedClusters({ clusters: result.data }))
}
