import React, { useEffect, useState } from "react";
import clsx from "clsx";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material ui components
import CircularProgress from "@material-ui/core/CircularProgress";
// jarr
import Cluster from "./components/Cluster";
import SelectedObjCard from "./components/SelectedObjCard";
import { doListClusters } from "./clusterSlice";
import clusterListStyle from "./clusterListStyle";


const filterClusters = (requestedClusterId, filter) => (cluster) => (
    // is selected cluster
    (requestedClusterId && requestedClusterId === cluster.id)
     // filters is on all
     || filter === "all"
     // cluster is not read and no filter
     || (!cluster.read && !filter)
     // cluster is liked and filtering on liked
     || (cluster.liked && filter === "liked")
);


function mapStateToProps(state) {
  let selectedFilterObj;
  if(state.clusters.filters["feed_id"]) {
    selectedFilterObj = state.feeds.feedListRows.filter((row) => (
      row.type === "feed" && row.id === state.clusters.filters["feed_id"]
    ))[0];
  } else if (state.clusters.filters["category_id"]) {
    selectedFilterObj = state.feeds.feedListRows.filter((row) => (
      row.type === "categ" && row.id === state.clusters.filters["category_id"]
    ))[0];
  }

  let clusters = [];
  if (!state.clusters.loading) {
    clusters = state.clusters.clusters.filter(
        filterClusters(state.clusters.requestedClusterId,
                       state.clusters.filters.filter)
    );
  }
  return { clusters,
           filters: state.clusters.filters,
           loading: state.clusters.loading,
           isShifted: state.feeds.isOpen && !state.edit.isOpen,
           selectedFilterObj,
  };
}

const mapDispatchToProps = (dispatch) => ({
  listClusters(filters) {
    return dispatch(doListClusters(filters));
  },
});


function ClusterList({ clusters, filters,
                       loading, isShifted,
                       selectedFilterObj,
                       listClusters, openEditPanel,
                       }) {
  const classes = clusterListStyle();
  const className = clsx(classes.content, {[classes.contentShift]: isShifted});
  const [everLoaded, setEverLoaded] = useState(false);
  useEffect(() => {
    if (!everLoaded) {
      setEverLoaded(true);
      listClusters(filters);
    }
  }, [everLoaded, filters, listClusters]);
  let content;
  if (loading) {
    content = <CircularProgress />;
  } else {
    content = clusters.map((cluster) => (
        <Cluster key={"c-" + cluster.id}
          id={cluster.id}
          read={cluster.read}
          liked={cluster.liked}
          mainTitle={cluster["main_title"]}
          mainLink={cluster["main_link"]}
          mainDate={cluster["main_date"]}
          mainFeedTitle={cluster.main_feed_title}
          feedsId={cluster["feeds_id"]}
          categoriesId={cluster["categories_id"]}
        />)
    );
  }

  return (
    <main className={className}>
      {selectedFilterObj ?
         <SelectedObjCard
           id={selectedFilterObj.id}
           str={selectedFilterObj.str}
           type={selectedFilterObj.type}
           iconUrl={selectedFilterObj["icon_url"]}
           errorCount={selectedFilterObj["error_count"]}
           lastRetrieved={selectedFilterObj["last_retrieved"]}
         /> : null}
      {content}
    </main>
  );
}

ClusterList.propTypes = {
  clusters: PropTypes.array.isRequired,
  filters: PropTypes.object.isRequired,
  loading: PropTypes.bool.isRequired,
  listClusters: PropTypes.func.isRequired,
  selectedFilterObj: PropTypes.object,
};

export default connect(mapStateToProps, mapDispatchToProps)(ClusterList);
