import React, { useEffect, useState } from "react";
import clsx from "clsx";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material ui components
import { useTheme } from "@material-ui/core/styles";
import Fab from "@material-ui/core/Fab";
import useMediaQuery from "@material-ui/core/useMediaQuery";
import CircularProgress from "@material-ui/core/CircularProgress";
import Paper from "@material-ui/core/Paper";
import AddIcon from "@material-ui/icons/Add";
import Alert from "@material-ui/lab/Alert";
// jarr
import Cluster from "./components/Cluster";
import Content from "./components/Content";
import SelectedObjCard from "./components/SelectedObjCard";
import { doListClusters, doLoadMoreClusters } from "./clusterSlice";
import makeStyles from "./components/style";


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
           loadedCluster: state.clusters.loadedCluster,
           filters: state.clusters.filters,
           loading: state.clusters.loading,
           isShifted: state.feeds.isOpen && !state.edit.isOpen,
           selectedFilterObj,
           doDisplayContent: (!!state.clusters.loadedCluster
              && !!state.clusters.requestedClusterId
              && !!state.clusters.loadedCluster.id
              && state.clusters.requestedClusterId === state.clusters.loadedCluster.id),
  };
}

const mapDispatchToProps = (dispatch) => ({
  listClusters(filters) {
    return dispatch(doListClusters(filters));
  },
  loadMoreClusters() {
    return dispatch(doLoadMoreClusters());
  },
});


function ClusterList({ clusters, filters, loadedCluster,
                       loading, isShifted, doDisplayContent,
                       selectedFilterObj,
                       listClusters, loadMoreClusters, openEditPanel,
                       }) {
  const theme = useTheme();
  const classes = makeStyles();
  const splitedMode = useMediaQuery(theme.breakpoints.up("md"));
  const contentClassName = clsx(classes.main,
    {[classes.mainShifted]: isShifted,
     [classes.mainSplitted]: splitedMode});
  const [everLoaded, setEverLoaded] = useState(false);
  useEffect(() => {
    if (!everLoaded) {
      setEverLoaded(true);
      listClusters(filters);
    }
  }, [everLoaded, filters, listClusters]);

  let list;
  let loadMoreButton;
  if (loading) {
    list = <div className={classes.loadingWrap}><CircularProgress /></div>;

  } else if (clusters.length) {
    list = clusters.map((cluster) => (
        <Cluster key={"c-" + cluster.id}
          cluster={cluster}
          splitedMode={splitedMode}
        />)
    );
    loadMoreButton = (
      <div className={classes.clusterLoadMore}>
        <Fab color="primary" className={classes.fab} onClick={loadMoreClusters}>
          <AddIcon />
        </Fab>
      </div>
    );
  } else {
    list = (<Alert severity="info">
      Nothing to read with the current filter. Try adding more feeds or come back later!
    </Alert>);
  }
  let card;
  if (selectedFilterObj) {
    card = <SelectedObjCard
              id={selectedFilterObj.id}
              str={selectedFilterObj.str}
              type={selectedFilterObj.type}
              iconUrl={selectedFilterObj["icon_url"]}
              errorCount={selectedFilterObj["error_count"]}
              lastRetrieved={selectedFilterObj["last_retrieved"]}
            />;
  }

  if (!splitedMode) {
    return (
      <main className={contentClassName}>
        {card}
        {list}
        {loadMoreButton}
      </main>
    );
  }
  return (
    <main className={contentClassName}>
      <div className={clsx(classes.clusterList,
                          {[classes.clusterListShifted]: isShifted,})}>
        <div className={classes.clusterListInner}>
          {card}
          {list}
          {loadMoreButton}
        </div>
      </div>
        {!doDisplayContent ? null :
          <Paper className={clsx(classes.contentPanel,
                                 {[classes.contentPanelShifted]: isShifted,})}>
            <div className={classes.contentPanelInner}>
              <Content clusterId={loadedCluster.id} />
            </div>
          </Paper>}
    </main>
  );
}

ClusterList.propTypes = {
  clusters: PropTypes.array.isRequired,
  filters: PropTypes.object.isRequired,
  loading: PropTypes.bool.isRequired,
  listClusters: PropTypes.func.isRequired,
  selectedFilterObj: PropTypes.object,
  doDisplayContent: PropTypes.bool.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(ClusterList);
