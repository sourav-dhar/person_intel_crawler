import { useState } from 'react';
import { SocialMediaProfile } from '../../types/search';

interface SocialMediaSectionProps {
  profiles: Record<string, SocialMediaProfile[]>;
}

const SocialMediaSection = ({ profiles }: SocialMediaSectionProps) => {
  const [activePlatform, setActivePlatform] = useState<string | null>(
    Object.keys(profiles)[0] || null
  );
  
  // Check if there are any profiles
  const hasSocialMedia = Object.keys(profiles).length > 0;
  
  if (!hasSocialMedia) {
    return (
      <div className="p-4 text-center text-gray-500">
        <p>No social media profiles found.</p>
      </div>
    );
  }
  
  const platformProfiles = activePlatform ? profiles[activePlatform] || [] : [];
  
  // Function to get platform icon class
  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'twitter':
        return 'fab fa-twitter text-blue-400';
      case 'linkedin':
        return 'fab fa-linkedin text-blue-700';
      case 'facebook':
        return 'fab fa-facebook text-blue-600';
      case 'instagram':
        return 'fab fa-instagram text-pink-600';
      case 'tiktok':
        return 'fab fa-tiktok text-black';
      case 'youtube':
        return 'fab fa-youtube text-red-600';
      case 'reddit':
        return 'fab fa-reddit text-orange-600';
      case 'github':
        return 'fab fa-github text-gray-800';
      default:
        return 'fas fa-user text-gray-500';
    }
  };
  
  return (
    <div className="p-4">
      <div className="mb-6 flex flex-wrap gap-2">
        {Object.keys(profiles).map((platform) => (
          <button
            key={platform}
            className={`px-4 py-2 rounded-md flex items-center space-x-2 ${
              activePlatform === platform
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
            onClick={() => setActivePlatform(platform)}
          >
            <i className={getPlatformIcon(platform)}></i>
            <span className="capitalize">{platform}</span>
            <span className="bg-white bg-opacity-20 px-2 py-0.5 rounded-full text-xs">
              {profiles[platform].length}
            </span>
          </button>
        ))}
      </div>

      <div>
        {platformProfiles.map((profile, index) => (
          <div
            key={`${profile.platform}-${profile.username}-${index}`}
            className="bg-white border border-gray-200 rounded-lg mb-4 overflow-hidden"
          >
            <div className="p-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
              <div className="flex items-center">
                <i className={`${getPlatformIcon(profile.platform)} mr-2 text-xl`}></i>
                <div>
                  <h3 className="font-medium text-gray-900">
                    {profile.display_name || profile.username}
                  </h3>
                  <p className="text-sm text-gray-500">@{profile.username}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {profile.is_verified && (
                  <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                    Verified
                  </span>
                )}
                <span className="bg-indigo-100 text-indigo-800 text-xs px-2 py-1 rounded-full">
                  Match: {Math.round(profile.relevance_score * 100)}%
                </span>
              </div>
            </div>
            
            <div className="p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                {profile.bio && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-1">Bio</h4>
                    <p className="text-sm text-gray-600">{profile.bio}</p>
                  </div>
                )}
                
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-1">Profile Info</h4>
                  <div className="text-sm text-gray-600 space-y-1">
                    {profile.location && (
                      <p>
                        <span className="font-medium">Location:</span> {profile.location}
                      </p>
                    )}
                    {profile.follower_count !== undefined && (
                      <p>
                        <span className="font-medium">Followers:</span>{' '}
                        {profile.follower_count.toLocaleString()}
                      </p>
                    )}
                    {profile.following_count !== undefined && (
                      <p>
                        <span className="font-medium">Following:</span>{' '}
                        {profile.following_count.toLocaleString()}
                      </p>
                    )}
                    {profile.post_count !== undefined && (
                      <p>
                        <span className="font-medium">Posts:</span>{' '}
                        {profile.post_count.toLocaleString()}
                      </p>
                    )}
                    {profile.joined_date && (
                      <p>
                        <span className="font-medium">Joined:</span>{' '}
                        {new Date(profile.joined_date).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                </div>
              </div>
              
              {profile.posts && profile.posts.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Recent Posts</h4>
                  <div className="space-y-2">
                    {profile.posts.slice(0, 3).map((post, postIndex) => (
                      <div
                        key={`post-${postIndex}`}
                        className="p-3 bg-gray-50 rounded-md text-sm text-gray-700"
                      >
                        <p>{post.text}</p>
                        <div className="mt-1 flex justify-between items-center text-xs text-gray-500">
                          {post.timestamp && (
                            <span>{new Date(post.timestamp).toLocaleString()}</span>
                          )}
                          {post.sentiment && (
                            <span
                              className={`px-2 py-0.5 rounded-full ${
                                post.sentiment === 'positive'
                                  ? 'bg-green-100 text-green-800'
                                  : post.sentiment === 'negative'
                                  ? 'bg-red-100 text-red-800'
                                  : post.sentiment === 'very_negative'
                                  ? 'bg-red-200 text-red-900'
                                  : 'bg-gray-100 text-gray-800'
                              }`}
                            >
                              {post.sentiment.replace('_', ' ')}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {profile.url && (
                <div className="mt-4 text-right">
                  <a
                    href={profile.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
                  >
                    View Full Profile →
                  </a>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SocialMediaSection;