import React from "react";
import PropTypes from "prop-types";
import { connect } from "react-redux";
// material ui components
import Typography from "@material-ui/core/Typography";
import Link from "@material-ui/core/Link";
import ExpansionPanel from "@material-ui/core/ExpansionPanel";
import ExpansionPanelSummary from "@material-ui/core/ExpansionPanelSummary";
import ExpansionPanelDetails from "@material-ui/core/ExpansionPanelDetails";
import ExpandMoreIcon from "@material-ui/icons/ExpandMore";
import CircularProgress from "@material-ui/core/CircularProgress";
import Checkbox from "@material-ui/core/Checkbox";
// material ui icons
import LikedIcon from '@material-ui/icons/Star';
import LikedIconBorder from '@material-ui/icons/StarBorder';
// jarr
import { doFetchCluster, doEditCluster, removeClusterSelection,
         updateClusterAttrs,
} from "../clusterSlice";
import makeStyles from "./clusterStyle";
import Articles from "./Articles";
import Article from "./Article";
import { changeReadCount } from "../../feedlist/feedSlice";
import FeedIcon from "../../../components/FeedIcon";

function mapStateToProps(state) {
  return { requestedClusterId: state.clusters.requestedClusterId,
           loadedCluster: state.clusters.loadedCluster,
           unreadOnClose: !state.clusters.filters.filter,
           icons: state.feeds.icons,
  };
}

const mapDispatchToProps = (dispatch) => ({
  handleClickOnPanel(e, clusterId, feedsId, categoriesId,
                     unreadOnClose, expanded) {
    if (!expanded) {
      // panel is folded, we fetch the cluster
      dispatch(doFetchCluster(clusterId));
      return dispatch(changeReadCount({ feedsId, categoriesId, action: "read" }));
    }
    if (unreadOnClose) {
      // panel is expanded and the filters implies
      // we have to mark cluster as unread
      dispatch(removeClusterSelection());
      dispatch(doEditCluster(clusterId,
                             { read: false, "read_reason": null }));
      return dispatch(changeReadCount(
          { feedsId, categoriesId, action: "unread" }));
    }
    // filters says everybody is displayed
    // so we're not triggering changes in cluster list
    return dispatch(removeClusterSelection());
  },
  toggleRead(e, clusterId, feedsId, categoriesId) {
    e.stopPropagation();
    const payload = { read: true, "read_reason": "marked" };
    let action = "read";
    if (!e.target.checked) {
      action = "unread";
      payload.read = false;
      payload["read_reason"] = null;
    }
    dispatch(doEditCluster(clusterId, payload));
    return dispatch(changeReadCount({ feedsId, categoriesId, action }));
  },
  toggleLiked(e, clusterId) {
    e.stopPropagation();
    return dispatch(doEditCluster(clusterId, { liked: e.target.checked }));
  },
  readOnRedirect(e, clusterId, feedsId, categoriesId) {
    e.stopPropagation();
    dispatch(updateClusterAttrs({ clusterId, read: true }));
    return dispatch(changeReadCount({ feedsId, categoriesId, action: "read" }));
  },
});

function Cluster({ id, read, liked, feedsId, categoriesId,
                   mainFeedTitle, mainTitle, mainLink, mainDate,
                   icons, requestedClusterId, loadedCluster, unreadOnClose,
                   readOnRedirect, toggleRead, toggleLiked,
                   handleClickOnPanel,
}) {
  const classes = makeStyles();
  const loaded = !!loadedCluster && loadedCluster.id === id;
  let content;
  if (id === requestedClusterId) {
    if (!loaded) {
      content = <CircularProgress />;
    } else if (loadedCluster.articles.length === 1) {
      content = <Article
                   article={loadedCluster.articles[0]}
                   hidden={false}
                 />;
    } else {
      content = <Articles
                   articles={loadedCluster.articles}
                   icons={icons}
                 />;
    }
  }
  const expanded = requestedClusterId === id;
  return (
      <ExpansionPanel
        expanded={expanded}
        onChange={(e) => handleClickOnPanel(e, id, feedsId, categoriesId,
                                            unreadOnClose, expanded)}
        TransitionProps={{ unmountOnExit: true }}
        key={"c"
             + (expanded ? "e" : "")
             + (read ? "r" : "")
             + (liked ? "l" : "")
             + id}
      >
        <ExpansionPanelSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1a-content"
          id="panel1a-header"
          key={"cs-" + id}
          className={classes.summary}
        >
          <div className={classes.link}>
            <Link href={mainLink} target="_blank"
              aria-label="link to the resource"
              onFocus={(e) => e.stopPropagation()}
              onClick={(e) => readOnRedirect(e, id, feedsId, categoriesId)}>
              {[ ...new Set(feedsId)].filter((feedId) => icons[feedId])
                      .map((feedId) => <FeedIcon
                                          key={"i" + id + "f" + feedId}
                                          iconUrl={icons[feedId]} />
                           )
              }
             {mainFeedTitle}
            </Link>
            <span>{mainDate}</span>
          </div>
          <div>
            <Checkbox checked={read} key={"c" + id + "r"}
              className={classes.titleAction}
              name="read" size="small" color="primary"
              aria-label="toggle read"
              onClick={(e) => e.stopPropagation()}
              onFocus={(e) => e.stopPropagation()}
              onChange={(e) => toggleRead(e, id, feedsId, categoriesId)} />
            <Checkbox checked={liked} key={"c" + id + "l"}
              className={classes.titleAction}
              name="liked" size="small" color="primary"
              aria-label="toggle read"
              icon={<LikedIconBorder />} checkedIcon={<LikedIcon />}
              onClick={(e) => e.stopPropagation()}
              onFocus={(e) => e.stopPropagation()}
              onChange={(e) => toggleLiked(e, id)} />
            <Typography className={classes.mainTitle}>
             {mainTitle}
            </Typography>
          </div>
        </ExpansionPanelSummary>
        <ExpansionPanelDetails
           className={classes.content}
           key={"cl-" + id}>
          {content}
        </ExpansionPanelDetails>
      </ExpansionPanel>
    );
}

Cluster.propTypes = {
  id: PropTypes.number.isRequired,
  read: PropTypes.bool.isRequired,
  liked: PropTypes.bool.isRequired,
  feedsId: PropTypes.array.isRequired,
  icons: PropTypes.object.isRequired,
  categoriesId: PropTypes.array,
  mainTitle: PropTypes.string.isRequired,
  mainLink: PropTypes.string.isRequired,
  mainFeedTitle: PropTypes.string.isRequired,
  mainDate: PropTypes.string.isRequired,
  unreadOnClose: PropTypes.bool.isRequired,
  requestedClusterId: PropTypes.number,
  loadedCluster: PropTypes.object,
  // funcs
  readOnRedirect: PropTypes.func.isRequired,
  toggleRead: PropTypes.func.isRequired,
  toggleLiked: PropTypes.func.isRequired,
  handleClickOnPanel: PropTypes.func.isRequired,
};

export default connect(mapStateToProps, mapDispatchToProps)(Cluster);
