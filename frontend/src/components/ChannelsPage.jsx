import React, { useState, useEffect } from 'react';
import { useDataContext } from '../context/Data';
import Channel from './Channel';

const Channels = () => {
    const {channelsData} = useDataContext();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (Object.keys(channelsData).length > 0) {
        setLoading(false); 
        }
    }, [channelsData]);

    if (loading) {
        return <></>; 
    }

  return (
    <div className="channel-grid">
        {Object.values(channelsData).map((channel, index) => (
            <Channel key={index}
                avatarSrc={channel.logo}
                channelName={channel.title}
                channelDescription={channel.description}
                channelSubscribers={channel.subscriberCount}
                channelVideoCount={channel.videoCount}
                channelID={channel._id}
                channelViewCount={channel.viewCount}
                action="remove"
            />
        ))}
    </div>
  );
};

export default Channels;



              