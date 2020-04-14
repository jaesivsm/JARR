import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux'

import Cluster from './Cluster';
import { doListClusters } from './clusterSlice';

function mapStateToProps(state) {
  return { clusters: state.clusters.clusters,
           filters: state.clusters.filters,
  };
};

const mapDispatchToProps = (dispatch) => ({
  listClusters(filters) {
    return dispatch(doListClusters(filters));
  },
});

function ClusterList({ clusters, filters, listClusters, className }) {
  const [everLoaded, setEverLoaded] = useState(false);
  useEffect(() => {
    if (!everLoaded) {
      setEverLoaded(true);
      listClusters(filters);
    }
  }, [everLoaded, filters, listClusters]);
  return (
    <main className={className}>
      {clusters.map((cluster) => (
        <Cluster key={"c-" + cluster.id}
          id={cluster.id}
          mainTitle={cluster.main_title}
          mainFeedTitle={cluster.main_feed_title}
        />
      ))}
    </main>);
}

ClusterList.propTypes = {
    clusters: PropTypes.array.isRequired,
    filters: PropTypes.object.isRequired,
    listClusters: PropTypes.func.isRequired,
    className: PropTypes.string.isRequired,
}

export default connect(mapStateToProps, mapDispatchToProps)(ClusterList);
