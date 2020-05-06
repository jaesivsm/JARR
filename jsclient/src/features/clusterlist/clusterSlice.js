import qs from "qs";
import { createSlice } from "@reduxjs/toolkit";
import { apiUrl, pageLength } from "../../const";
import { doRetryOnTokenExpiration } from "../../authSlice";

export const filterClusters = (requestedClusterId, filter) => (cluster) => (
    // is selected cluster
    (requestedClusterId && requestedClusterId === cluster.id)
     // filters is on all
     || filter === "all"
     // cluster is not read and no filter
     || (!cluster.read && !filter)
     // cluster is liked and filtering on liked
     || (cluster.liked && filter === "liked")
);

const clusterSlice = createSlice({
  name: "cluster",
  initialState: { filters: { },
                  requestedFilter: "",
                  loading: false,
                  moreLoading: false,
                  moreToFetch: true,
                  clusters: [],
                  requestedClusterId: null,
                  loadedCluster: {},
  },
  reducers: {
    requestedClustersList(state, action) {
      const filters = { ...state.filters };
      if (filters["from_date"]) {
        delete filters["from_date"];
      }
      if (action.payload.filters.feedId
          || action.payload.filters.categoryId === "all") {
        delete filters["category_id"];
      }
      if (action.payload.filters.feedId) {
        filters["feed_id"] = action.payload.filters.feedId;
      } else if (action.payload.filters.categoryId) {
        if (action.payload.filters.categoryId !== "all" ) {
          filters["category_id"] = action.payload.filters.categoryId;
        }
        if (filters["feed_id"]) {
          delete filters["feed_id"];
        }
      }
      if (action.payload.filters.filter) {
        filters.filter = action.payload.filters.filter;
      } else if (action.payload.filters.filter === null) {
        delete filters.filter;
      }
      return { ...state, filters, loading: true, clusters: [],
               requestedFilter: qs.stringify(filters),
      };
    },
    requestedMoreCLusters(state, action) {
      const filters = { ...state.filters,
                        "from_date": state.clusters[state.clusters.length - 1].main_date };
      return { ...state, filters, moreLoading: true,
               requestedFilter: qs.stringify(filters),
      };
    },
    retrievedClustersList(state, action) {
      if (action.payload.requestedFilter !== state.requestedFilter) {
        // dispatch from an earlier request that has been ignored
        return state;  // ignoring
      }
      if (action.payload.strat === "append") {
        return { ...state, loading: false, moreLoading: false,
                 moreToFetch: action.payload.clusters.length >= pageLength,
                 clusters: [ ...state.clusters, ...action.payload.clusters],
        };
      }
      return { ...state, loading: false, moreLoading: false,
               moreToFetch: action.payload.clusters.length >= pageLength,
               clusters: action.payload.clusters };
    },
    requestedCluster(state, action) {
      return { ...state,
               requestedClusterId: action.payload.clusterId,
               loadedCluster: {},
      };
    },
    retrievedCluster(state, action) {
      if (state.requestedClusterId !== action.payload.cluster.id) {
        return state; // not the object that was asked for last, ignoring
      }
      return { ...state,
               // marking retrived cluster as read
               clusters: state.clusters.map((cluster) => {
                 if(cluster.id === action.payload.cluster.id) {
                    return { ...cluster, read: true };
                 }
                 return cluster;
               }),
               loadedCluster: action.payload.cluster,
      };
    },
    updateClusterAttrs(state, action) {
      const alterCluster = (cluster) => {
        if (cluster.id === action.payload.clusterId) {
          return { ...cluster,
                   read: action.payload.read === undefined ? cluster.read : action.payload.read,
                   liked: action.payload.liked === undefined ? cluster.liked : action.payload.liked };
          }
          return cluster;
      };
      return { ...state,
               // marking updated cluster as unread
               clusters: state.clusters.map(alterCluster),
      };
    },
    removeClusterSelection(state, action) {
      return { ...state, loadedCluster: {}, requestedClusterId: null };
    },
    markedAllAsRead(state, action) {
      return { ...state, clusters: [] };
    },
  },
});

export const { requestedClustersList, retrievedClustersList,
               requestedCluster, retrievedCluster,
               requestedMoreCLusters,
               updateClusterAttrs,
               removeClusterSelection,
               markedAllAsRead,
} = clusterSlice.actions;
export default clusterSlice.reducer;

export const doListClusters = (filters): AppThunk => async (dispatch, getState) => {
  dispatch(requestedClustersList({ filters }));
  const requestedFilter = getState().clusters.requestedFilter;
  const result = await doRetryOnTokenExpiration({
    method: "get",
    url: apiUrl + "/clusters?" + requestedFilter,
  }, dispatch, getState);
  dispatch(retrievedClustersList({ requestedFilter, clusters: result.data,
                                   strat: "replace" }));
};

export const doLoadMoreClusters = (): AppThunk => async (dispatch, getState) => {
  dispatch(requestedMoreCLusters());
  const requestedFilter = getState().clusters.requestedFilter;
  const result = await doRetryOnTokenExpiration({
    method: "get",
    url: apiUrl + "/clusters?" + requestedFilter,
  }, dispatch, getState);
  dispatch(retrievedClustersList({ requestedFilter, clusters: result.data,
                                   strat: "append" }));
};

export const doFetchCluster = (clusterId): AppThunk => async (dispatch, getState) => {
  dispatch(requestedCluster({ clusterId }));
  const result = await doRetryOnTokenExpiration({
    method: "get",
    url: apiUrl + "/cluster/" + clusterId,
  }, dispatch, getState);
  dispatch(retrievedCluster({ cluster: result.data }));
};

export const doEditCluster = (clusterId, payload): AppThunk => async (dispatch, getState) => {
  dispatch(updateClusterAttrs({ clusterId, ...payload }));
  if (payload["read_reason"] === null) {
    delete payload["read_reason"];
  }
  await doRetryOnTokenExpiration({
    method: "put",
    url: apiUrl + "/cluster/" + clusterId,
    data: payload,
  }, dispatch, getState);
  const clusterState = getState().clusters;
  if (clusterState.moreToFetch && clusterState.clusters.filter(
        filterClusters(clusterState.requestedClusterId,
                       clusterState.filters.filter)
      ).length === (pageLength / 3 * 2)) {
    dispatch(doLoadMoreClusters());
  }
};
