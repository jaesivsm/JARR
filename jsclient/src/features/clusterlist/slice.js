import qs from "qs";
import { createSlice } from "@reduxjs/toolkit";
import { pageLength } from "../../const";

export const showCluster = (cluster, requestedClusterId, filter) => (
  // is selected cluster
  (requestedClusterId && requestedClusterId === cluster.id)
   // filters is on all
   || filter === "all"
   // cluster is not read and no filter
   || (!cluster.read && !filter)
   // cluster is liked and filtering on liked
   || (cluster.liked && filter === "liked")
);

export const filterClusters = (requestedClusterId, filter) => (
    (cluster) => showCluster(cluster, requestedClusterId, filter));

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
    requestedClustersList: (state, action) => {
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
    requestedMoreCLusters: (state, action) => {
      const filters = { ...state.filters,
                        "from_date": state.clusters[state.clusters.length - 1].main_date };
      return { ...state, filters, moreLoading: true,
               requestedFilter: qs.stringify(filters),
      };
    },
    retrievedClustersList: (state, action) => {
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
    requestedCluster: (state, action) => ({
      ...state,
      requestedClusterId: action.payload.clusterId,
      loadedCluster: {},
    }),
    retrievedCluster: (state, action) => {
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
    updateClusterAttrs: (state, action) => {
      const alterCluster = (cluster) => {
        if (cluster.id === action.payload.clusterId) {
          return { ...cluster,
                   read: typeof(action.payload.read) === "undefined" ? cluster.read : action.payload.read,
                   liked: typeof(action.payload.liked) === "undefined" ? cluster.liked : action.payload.liked };
          }
          return cluster;
      };
      return { ...state,
               // marking updated cluster as unread
               clusters: state.clusters.map(alterCluster),
      };
    },
    removeClusterSelection: (state, action) => ({
      ...state, loadedCluster: {}, requestedClusterId: null,
    }),
    markedAllAsRead: (state, action) => {
      if (!action.payload.onlySingles) {
        return { ...state, clusters: [] };
      }
      return { ...state,
               clusters: state.clusters.filter((cluster) =>
                 cluster["feeds_id"].length > 1),
      };
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
