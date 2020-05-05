import React from "react";
import clsx from "clsx";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import moment from "moment";
// material ui components
import Typography from "@material-ui/core/Typography";
import Link from "@material-ui/core/Link";
import ExpansionPanel from "@material-ui/core/ExpansionPanel";
import ExpansionPanelSummary from "@material-ui/core/ExpansionPanelSummary";
import ExpansionPanelDetails from "@material-ui/core/ExpansionPanelDetails";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import Checkbox from "@material-ui/core/Checkbox";
// material ui icons
import LikedIcon from "@material-ui/icons/Star";
import LikedIconBorder from "@material-ui/icons/StarBorder";
// jarr
import { doFetchCluster, doEditCluster, removeClusterSelection,
} from "../clusterSlice";
import makeStyles from "./style";
import { changeReadCount } from "../../feedlist/feedSlice";
import ClusterIcon from "../../../components/ClusterIcon";
import Content from "./Content";

function mapStateToProps(state) {
  return { requestedClusterId: state.clusters.requestedClusterId,
           unreadOnClose: !state.clusters.filters.filter,
           icons: state.feeds.icons,
  };
}

const mapDispatchToProps = (dispatch) => ({
  handleClickOnPanel(e, cluster, unreadOnClose, expanded) {
    if (!expanded) {
      // panel is folded, we fetch the cluster
      dispatch(doFetchCluster(cluster.id));
      return dispatch(changeReadCount({
        feedsId: cluster["feeds_id"],
        categoriesId: cluster["categories_id"],
        action: "read" }));
    }
    if (unreadOnClose) {
      // panel is expanded and the filters implies
      // we have to mark cluster as unread
      dispatch(removeClusterSelection());
      dispatch(doEditCluster(cluster.id,
                             { read: false, "read_reason": null }));
      return dispatch(changeReadCount(
          { feedsId: cluster["feeds_id"],
            categoriesId: cluster["categories_id"],
            action: "unread" }));
    }
    // filters says everybody is displayed
    // so we"re not triggering changes in cluster list
    return dispatch(removeClusterSelection());
  },
  toggleRead(e, cluster) {
    e.stopPropagation();
    const payload = { read: true, "read_reason": "marked" };
    let action = "read";
    if (!e.target.checked) {
      action = "unread";
      payload.read = false;
      payload["read_reason"] = null;
    }
    dispatch(doEditCluster(cluster.id, payload));
    return dispatch(changeReadCount({
      feedsId: cluster["feeds_id"],
      categoriesId: cluster["categories_id"], action }));
  },
  toggleLiked(e, clusterId) {
    e.stopPropagation();
    return dispatch(doEditCluster(clusterId, { liked: e.target.checked }));
  },
  readOnRedirect(e, cluster) {
    e.stopPropagation();
    dispatch(doEditCluster(cluster.id,
                           { read: false, "read_reason": "consulted" }));
    return dispatch(changeReadCount({
      feedsId: cluster["feeds_id"],
      categoriesId: cluster["categories_id"],
      action: "read" }));
  },
});

function Cluster({ cluster,
                   icons, requestedClusterId, unreadOnClose,
                   readOnRedirect, toggleRead, toggleLiked,
                   handleClickOnPanel, splitedMode,
}) {
  const classes = makeStyles();
  const expanded = requestedClusterId === cluster.id;
  return (
      <ExpansionPanel
        expanded={expanded}
        elevation={expanded ? 10: 2}
        TransitionProps={{ unmountOnExit: true }}
        key={"c"
             + (expanded ? "e" : "")
             + (cluster.read ? "r" : "")
             + (cluster.liked ? "l" : "")
             + cluster.id}
        onChange={(e) => handleClickOnPanel(e, cluster,
                                            unreadOnClose, expanded)}
      >
        <ExpansionPanelSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1a-content"
          id="panel1a-header"
          key={"cs-" + cluster.id}
          className={classes.summary}
        >
          <div className={classes.link}>
            <Link href={cluster["main_link"]} target="_blank"
              aria-label="link to the resource"
              color="secondary"
              onFocus={(e) => e.stopPropagation()}
              onClick={(e) => readOnRedirect(e, cluster)}>
              {[ ...new Set(cluster["feeds_id"])].filter((feedId) => icons[feedId])
                      .map((feedId) => <ClusterIcon
                                          key={"i" + cluster.id + "f" + feedId}
                                          iconUrl={icons[feedId]} />
                           )
              }
             {cluster["main_feed_title"]}
            </Link>
            <span className={classes.clusterDate}>{moment(cluster["main_date"]).fromNow()}</span>
          </div>
          <div>
            <Checkbox checked={cluster.read} key={"c" + cluster.id + "r"}
              className={classes.titleAction}
              name="read" size="small" color="primary"
              aria-label="toggle read"
              onClick={(e) => e.stopPropagation()}
              onFocus={(e) => e.stopPropagation()}
              onChange={(e) => toggleRead(e, cluster)} />
            <Checkbox checked={cluster.liked} key={"c" + cluster.id + "l"}
              className={classes.titleAction}
              name="liked" size="small" color="primary"
              aria-label="toggle read"
              icon={<LikedIconBorder />} checkedIcon={<LikedIcon />}
              onClick={(e) => e.stopPropagation()}
              onFocus={(e) => e.stopPropagation()}
              onChange={(e) => toggleLiked(e, cluster.id)} />
            <Typography
               className={clsx(classes.mainTitle, {[classes.mainTitleExpanded]: expanded})}>
             {cluster["main_title"]}
            </Typography>
          </div>
        </ExpansionPanelSummary>
          {!splitedMode ? (<ExpansionPanelDetails
           className={classes.content}
           key={"cl-" + cluster.id}>
           <Content clusterId={cluster.id} />
        </ExpansionPanelDetails>): null}
      </ExpansionPanel>
    );
}

Cluster.propTypes = {
  cluster: PropTypes.shape({
    id: PropTypes.number.isRequired,
    read: PropTypes.bool.isRequired,
    liked: PropTypes.bool.isRequired,
    "feeds_id": PropTypes.array.isRequired,
    "categories_id": PropTypes.array.isRequired,
    "main_title": PropTypes.string.isRequired,
    "main_link": PropTypes.string.isRequired,
    "main_feed_title": PropTypes.string.isRequired,
    "main_date": PropTypes.string.isRequired,
  }),
  icons: PropTypes.object.isRequired,
  unreadOnClose: PropTypes.bool.isRequired,
  requestedClusterId: PropTypes.number,
  splitedMode: PropTypes.bool.isRequired,
  // funcs
  readOnRedirect: PropTypes.func.isRequired,
  toggleRead: PropTypes.func.isRequired,
  toggleLiked: PropTypes.func.isRequired,
  handleClickOnPanel: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(Cluster);
