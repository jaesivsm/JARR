import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux'
import Typography from '@material-ui/core/Typography';
import Link from '@material-ui/core/Link';
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';

import { doFetchClusters } from './clusterSlice';

function mapStateToProps(state) {
  return { clusters: state.clusters.clusters,
           filters: state.clusters.filters,
  };
};

const mapDispatchToProps = (dispatch) => ({
  fetchClusters(filters) {
    return dispatch(doFetchClusters(filters));
  },
});

function ClusterList({ clusters, filters, fetchClusters }) {
  const [everLoaded, setEverLoaded] = useState(false);
  useEffect(() => {
    if (!everLoaded) {
      setEverLoaded(true);
      fetchClusters(filters);
    }
  }, [everLoaded, filters, fetchClusters]);
  return (
    <>
      {clusters.map((cluster) => (
      <ExpansionPanel key={"c-" + cluster.id}>
        <ExpansionPanelSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1a-content"
          id="panel1a-header"
          key={"cs-" + cluster.id}
        >
          <Link href="/">
           {cluster.main_feed_title}
          </Link>
          <Typography>
           {cluster.main_title}
          </Typography>
        </ExpansionPanelSummary>
        <ExpansionPanelDetails
            key={"cl-" + cluster.id}>
          <Typography>
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse malesuada lacus ex,
            sit amet blandit leo lobortis eget.
          </Typography>
        </ExpansionPanelDetails>
      </ExpansionPanel>
      ))}
    </>);
}

ClusterList.propTypes = {
    clusters: PropTypes.array.isRequired,
    filters: PropTypes.object.isRequired,
    fetchClusters: PropTypes.func.isRequired,
}

export default connect(mapStateToProps, mapDispatchToProps)(ClusterList);
