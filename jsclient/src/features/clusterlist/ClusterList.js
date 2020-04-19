import React, { useEffect, useState } from "react";
import clsx from "clsx";
import PropTypes from "prop-types";
import { connect } from "react-redux";

import Card from "@material-ui/core/Card";
import CardActions from "@material-ui/core/CardActions";
import CardContent from "@material-ui/core/CardContent";
import Button from "@material-ui/core/Button";

import Cluster from "./Cluster";
import { doListClusters } from "./clusterSlice";
import { doFetchObjForEdit } from "../editpanel/editSlice";
import clusterListStyle from "./clusterListStyle";

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
  return { clusters: state.clusters.clusters,
           filters: state.clusters.filters,
           selectedClusterId: state.clusters.requestedClusterId,
           isShifted: state.feeds.isOpen && !state.edit.isOpen,
           selectedFilterObj,
  };
}

const mapDispatchToProps = (dispatch) => ({
  listClusters(filters) {
    return dispatch(doListClusters(filters));
  },
  openEditPanel(objType, objId) {
    return dispatch(doFetchObjForEdit(objType, objId));
  },
});

function ClusterList({ clusters, filters, listClusters, openEditPanel,
                       isShifted, selectedClusterId, selectedFilterObj }) {
  const classes = clusterListStyle();
  const className = clsx(classes.content, {[classes.contentShift]: isShifted});
  const [everLoaded, setEverLoaded] = useState(false);
  useEffect(() => {
    if (!everLoaded) {
      setEverLoaded(true);
      listClusters(filters);
    }
  }, [everLoaded, filters, listClusters]);

  let card = null;
  if(selectedFilterObj) {
      const objType = selectedFilterObj.type === "feed" ? "feed" : "category";
      card = (
        <Card variant="outlined">
          <CardContent>
            {selectedFilterObj.str}
          </CardContent>
          <CardActions>
            <Button size="small"
              onClick={() => openEditPanel(objType, selectedFilterObj.id)}
          >
              Edit {objType}
            </Button>
          </CardActions>
        </Card>
      );
  }
  return (
    <main className={className}>
      {card}
      {clusters.filter((cluster) => {
        return (// is selected cluster
                (selectedClusterId && selectedClusterId === cluster.id)
                // filters is on all
                || filters.filter === "all"
                // cluster is not read and no filter
                || (!cluster.read && !filters.filter)
                // cluster is liked and filtering on liked
                || (cluster.liked && filters.filter === "liked"));
       }).map((cluster) => (
         <Cluster key={"c-" + cluster.id}
           id={cluster.id}
           mainTitle={cluster.main_title}
           mainFeedTitle={cluster.main_feed_title}
         />
      ))}
    </main>
  );
}

ClusterList.propTypes = {
  clusters: PropTypes.array.isRequired,
  filters: PropTypes.object.isRequired,
  selectedClusterId: PropTypes.number,
  listClusters: PropTypes.func.isRequired,
  openEditPanel: PropTypes.func.isRequired,
  selectedFilterObj: PropTypes.object,
};

export default connect(mapStateToProps, mapDispatchToProps)(ClusterList);
