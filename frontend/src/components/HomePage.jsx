import React, { useState, useEffect } from 'react';
import { useDataContext } from '../context/Data';
import Video from './Video';

const Home = () => {
  const { videosData, channelsData } = useDataContext();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (videosData.length > 0 && Object.keys(channelsData).length > 0) {
      setLoading(false); 
    }
  }, [videosData, channelsData]);

  if (loading) {
    return <></>; 
  }

  return (
    <div className="video-grid">
      {videosData.filter(video => video.viewed === 0).map((video, index) => (
          <Video key={index}
              cardImageSrc={video.thumbnail}
              avatarSrc={channelsData[video.channel].logo}
              videoTitle={video.title}
              videoDuration={video.duration}
              channelName={channelsData[video.channel].title}
              channelSubscribers={channelsData[video.channel].subscriberCount}
              videoPublished={video.published}
              videoID={video._id}
              channelID={video.channel}
              viewed={video.viewed}
          />
      ))}
    </div>
  );
};

export default Home;



              