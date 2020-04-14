import axios from 'axios';
import { createSlice } from '@reduxjs/toolkit';
import { apiUrl } from '../../const.js';

const feedSlice = createSlice({
  name: 'feed',
  initialState: { loading: false,
                  categories: [],
  },
  reducers: {
    askedFeeds(state, action) {
      return { ...state, loading: true };
    },
    loadedFeeds(state, action) {
      const categories = action.payload.categories.map((cat) => (
            { ...cat, isFolded: false }));
      return { ...state, loading: false, categories };
    },
  },
});

export const { askedFeeds, loadedFeeds } = feedSlice.actions;
export default feedSlice.reducer;

export const doFetchFeeds = (
): AppThunk => async (dispatch, getState) => {
  dispatch(askedFeeds());
  const result = await axios({
    method: 'get',
    url: apiUrl + '/list-feeds',
    headers: { 'Authorization': getState().login.token },
  });
  dispatch(loadedFeeds({ categories: result.data }))
}
