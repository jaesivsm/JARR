import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material ui components
import makeStyles from "./style";
import CircularProgress from "@material-ui/core/CircularProgress";
// jarr
import Articles from "./Articles";
import Article from "./Article";

function mapStateToProps(state) {
  return { loadedCluster: state.clusters.loadedCluster,
           unreadOnClose: !state.clusters.filters.filter,
           icons: state.feeds.icons,
  };
}

function Content({ clusterId, loadedCluster, icons }) {
  const classes = makeStyles();
  if (loadedCluster.id !== clusterId) {
    return <div className={classes.loadingWrap}><CircularProgress /></div>;
  } else if (loadedCluster.articles.length === 1) {
    return (<Article article={loadedCluster.articles[0]}
                     hidden={false} />);
  } else {
    return (<Articles articles={loadedCluster.articles}
                      icons={icons} />);
  }
}

Content.propTypes = {
  clusterId: PropTypes.number,
  loadedCluster: PropTypes.object,
};

export default connect(mapStateToProps)(Content);
