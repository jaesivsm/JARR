import React, { useEffect } from "react";
import { connect } from "react-redux";
import { useParams } from "react-router-dom";
import ClusterList from "./features/clusterlist/ClusterList";
import doListClusters from "./hooks/doListClusters";
import doFetchCluster from "./hooks/doFetchCluster";

const mapDispatchToProps = (dispatch) => ({
  listClusters(filters) {
    dispatch(doListClusters(filters));
  },
  fetchCluster(clusterId) {
    dispatch(doFetchCluster(clusterId));
  },
});

function MainView({ listClusters, fetchCluster }) {
  const { feedId, categoryId, clusterId } = useParams();

  useEffect(() => {
    if (feedId) {
      listClusters({ feedId: parseInt(feedId) });
    } else if (categoryId) {
      listClusters({ categoryId: categoryId === "all" ? "all" : parseInt(categoryId) });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [feedId, categoryId]);

  useEffect(() => {
    if (clusterId) {
      fetchCluster(parseInt(clusterId));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clusterId]);

  return <ClusterList />;
}

export default connect(null, mapDispatchToProps)(MainView);
