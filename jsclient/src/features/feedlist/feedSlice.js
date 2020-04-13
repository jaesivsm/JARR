import axios from 'axios';
import { createSlice } from '@reduxjs/toolkit';
import { apiUrl } from '../../const.js';

const feedSlice = createSlice({
  name: 'feed',
  initialState: { loading: false,
                  categories: [],
                  everLoaded: false,
  },
  reducers: {
    askedFeeds(state, action) {
        return { ...state, loading: true, everLoaded: true };
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
  token: string,
): AppThunk => async dispatch => {
  dispatch(askedFeeds());
  const result = await axios.get(
      apiUrl + '/list-feeds',
      {
        headers: { 'Authorization': token }},
      { responseType: 'json',
        headers: { 'Authorization': token }},
  );
  console.log(result);
    console.log(result.data);
  dispatch(loadedFeeds({ categories: result.data }))
}
