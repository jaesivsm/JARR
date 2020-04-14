import axios from "axios";
import qs from "qs";
import { createSlice } from "@reduxjs/toolkit";
import { apiUrl } from "../../const";

const clusterSlice = createSlice({
  name: "cluster",
  initialState: { filters: {},
                  loadingClusterList: false,
                  clusters: [],
                  selected: {},
                  requestedClusterId: null,
                  loadedCluster: {},
  },
  reducers: {
    requestedClustersList(state, action) {
      const selected = {};
      const filters = {};
      if (action.payload.filters.feedId) {
        selected.feedId = filters["feed_id"] = action.payload.filters.feedId;

      } else if (action.payload.filters.categoryId) {
        selected.categoryId = filters["category_id"] = action.payload.filters.categoryId;
      }

      return { ...state, filters, selected, loadingClusterList: true };
    },
    retrievedClustersList(state, action) {
      return { ...state, loadingClusterList: false,
               clusters: action.payload.clusters };
    },
    requestedCluster(state, action) {
      return { ...state,
               requestedClusterId: action.payload.clusterId,
               loadedCluster: {},
      };
    },
    retrievedCluster(state, action) {
        // TODO remove old cluster
      return { ...state,
               loadedCluster: action.payload.cluster,
      };
    },
    requestedUnreadCluster(state, action) {
      return { ...state,
               loadedCluster: {}, requestedClusterId: null,
      };
    },
    retrievedUnreadCluster(state, action) {
      return state;
    },
  },
});

export const { requestedClustersList, retrievedClustersList,
               requestedCluster, retrievedCluster,
               requestedUnreadCluster, retrievedUnreadCluster,
} = clusterSlice.actions;
export default clusterSlice.reducer;

export const doListClusters = (filters): AppThunk => async (dispatch, getState) => {
  dispatch(requestedClustersList({ filters }));
  const params = qs.stringify(getState().clusters.filters);
  const result = await axios({
    method: "get",
    url: apiUrl + "/clusters?" + params,
    headers: { "Authorization": getState().login.token },
  });
  dispatch(retrievedClustersList({ clusters: result.data }));
};

export const doReadCluster = (clusterId): AppThunk => async (dispatch, getState) => {
  dispatch(requestedCluster({ clusterId }));
  const result = await axios({
    method: "get",
    url: apiUrl + "/cluster/" + clusterId,
    headers: { "Authorization": getState().login.token },
  });
  dispatch(retrievedCluster({ cluster: result.data }));
};

export const doUnreadCluster = (clusterId): AppThunk => async (dispatch, getState) => {
  dispatch(requestedUnreadCluster({ clusterId }));
  await axios({
    method: "put",
    url: apiUrl + "/cluster/" + clusterId + "?read=false",
    headers: { "Authorization": getState().login.token },
  });
  dispatch(retrievedUnreadCluster());
};
