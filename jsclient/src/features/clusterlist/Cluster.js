import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux'
import Typography from '@material-ui/core/Typography';
import Link from '@material-ui/core/Link';
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import CircularProgress from '@material-ui/core/CircularProgress';

import { doReadCluster } from './clusterSlice';

function mapStateToProps(state) {
  return { requestedClusterId: state.clusters.requestedClusterId,
           loadedCluster: state.clusters.loadedCluster,
  };
};

const mapDispatchToProps = (dispatch) => ({
  readCluster(clusterId) {
    return dispatch(doReadCluster(clusterId));
  },
});

function Cluster({ id, main_feed_title, main_title, requestedClusterId, loadedCluster, readCluster }) {
  const expanded = requestedClusterId === id;
  const loaded = !!loadedCluster && loadedCluster.id === id;
  let content;
  if (id === requestedClusterId) {
    if (!loaded) {
      content = <CircularProgress />;
    } else if (loaded) {
      content = (
        <Typography>
          {loadedCluster.articles[0].content}
        </Typography>
      );
    }
  }
  return (
      <ExpansionPanel
        expanded={expanded}
        onChange={() => {
          if (!expanded) {
            readCluster(id);
          } //TODO mark as unread
        }}
      >
        <ExpansionPanelSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1a-content"
          id="panel1a-header"
          key={"cs-" + id}
        >
          <Link href="/">
           {main_feed_title}
          </Link>
          <Typography>
           {main_title}
          </Typography>
        </ExpansionPanelSummary>
        <ExpansionPanelDetails key={"cl-" + id}>
          {content}
        </ExpansionPanelDetails>
      </ExpansionPanel>
    );
};

Cluster.propTypes = {
  id: PropTypes.number.isRequired,
  main_title: PropTypes.string.isRequired,
  main_feed_title: PropTypes.string.isRequired,
  requestedClusterId: PropTypes.number,
  loadedCluster: PropTypes.object,
};

export default connect(mapStateToProps, mapDispatchToProps)(Cluster);
