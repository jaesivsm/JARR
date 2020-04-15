import { doRetryOnTokenExpiration } from "../login/userSlice";
import qs from "qs";
import { createSlice } from "@reduxjs/toolkit";
import { apiUrl } from "../../const";

const clusterSlice = createSlice({
  name: "cluster",
  initialState: { filters: { },
                  loading: false,
                  clusters: [],
                  requestedClusterId: null,
                  loadedCluster: {},
  },
  reducers: {
    requestedClustersList(state, action) {
      const filters = { ...state.filters };
      if (action.payload.filters.feedId
          || action.payload.filters.categoryId === "all") {
        delete filters['category_id'];
      }
      if (action.payload.filters.feedId) {
        filters["feed_id"] = action.payload.filters.feedId;

      } else if (action.payload.filters.categoryId) {
        if (action.payload.filters.categoryId !== "all" ) {
          filters["category_id"] = action.payload.filters.categoryId;
        }
        if (filters["feed_id"]) {
          delete filters['feed_id'];
        }
      }
      if (action.payload.filters.filter) {
        filters.filter = action.payload.filters.filter;
      } else if (action.payload.filters.filter === null) {
        delete filters.filter;
      }
      return { ...state, filters, loading: true};
    },
    retrievedClustersList(state, action) {
      return { ...state, loading: false,
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
  const result = await doRetryOnTokenExpiration({
    method: "get",
    url: apiUrl + "/clusters?" + params,
  }, dispatch, getState);
  dispatch(retrievedClustersList({ clusters: result.data }));
};

export const doReadCluster = (clusterId): AppThunk => async (dispatch, getState) => {
  dispatch(requestedCluster({ clusterId }));
  const result = await doRetryOnTokenExpiration({
    method: "get",
    url: apiUrl + "/cluster/" + clusterId,
  }, dispatch, getState);
  dispatch(retrievedCluster({ cluster: result.data }));
};

export const doUnreadCluster = (clusterId): AppThunk => async (dispatch, getState) => {
  dispatch(requestedUnreadCluster({ clusterId }));
  await doRetryOnTokenExpiration({
    method: "put",
    url: apiUrl + "/cluster/" + clusterId + "?read=false",
  }, dispatch, getState);
  dispatch(retrievedUnreadCluster());
};
