import React, { useState, useEffect } from 'react';
import { useDataContext } from '../context/Data';
import Channel from './Channel';

const Channels = () => {
    const {channelsData} = useDataContext();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (Object.keys(channelsData).length > 0) {
        setLoading(false); 
        console.log(channelsData)
        }
    }, [channelsData]);

    if (loading) {
        return <></>; 
    }

  return (
    <div className="channel-grid">
        {Object.values(channelsData).sort((a, b) => b.subscriberCount - a.subscriberCount).map((channel, index) => (
            <Channel key={index}
                avatarSrc={channel.logo}
                channelName={channel.title}
                channelDescription={channel.description}
                channelSubscribers={channel.subscriberCount}
                channelVideoCount={channel.videoCount}
                channelID={channel._id}
                channelViewCount={channel.viewCount}
                action="remove"
                stats="true"
            />
        ))}
    </div>
  );
};

export default Channels;



              