import { useState, useEffect } from 'react';
import { TextInput, Button, Avatar, Container, Group, FileInput, Notification } from '@mantine/core';
import { api } from '../utils/api/axios';

interface Profile {
  firstName: string;
  lastName: string;
  email: string;
  phoneNumber: string;
  address: string;
  avatar: string;
  userId: string;
}

const Profile = () => {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [editedProfile, setEditedProfile] = useState<Partial<Profile>>({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);

  useEffect(() => {
    api.get('/dashboard/profile', {
      headers: { Authorization: `Bearer ${sessionStorage.getItem('token')}` }
    })
    .then((response) => {
      setProfile(response.data.profile);
    })
    .catch(() => setError('Failed to load profile'));
  }, []);

  const handleChange = (field: keyof Profile, value: string) => {
    setEditedProfile((prev) => ({ ...prev, [field]: value }));
  };

  const handleAvatarUpload = (file: File | null) => {
    if (!file) return;
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = reader.result as string;
      setEditedProfile((prev) => ({ ...prev, avatar: base64String }));
    };
    reader.readAsDataURL(file);
  };

  const handleSave = () => {
    setSaving(true);
    api.put('/dashboard/profile', editedProfile, {
      headers: { Authorization: `Bearer ${sessionStorage.getItem('token')}` }
    })
    .then(() => {
      setProfile((prev) => ({ ...prev, ...editedProfile } as Profile));
      setEditedProfile({});
      setEditMode(false);
    })
    .catch(() => setError('Failed to save profile'))
    .finally(() => setSaving(false));
  };

  const handleCancel = () => {
    setEditedProfile({});
    setEditMode(false);
  };

  return (
    <Container>
      {error && <Notification color="red">{error}</Notification>}
      {profile && (
        <>
          <Group>
            <Avatar src={editedProfile.avatar ?? profile.avatar} size={100} radius="xl" />
            {editMode && (
              <FileInput placeholder="Upload new avatar" onChange={handleAvatarUpload} />
            )}
          </Group>

          <TextInput variant="filled" size="md" label="User ID" disabled value={profile.userId} />
          <TextInput variant="filled" size="md" label="First Name" disabled value={profile.firstName} />
          <TextInput variant="filled" size="md" label="Last Name" disabled value={profile.lastName} />
          <TextInput 
            variant="filled" size="md"
            label="Phone Number" 
            disabled={!editMode} 
            value={editedProfile.phoneNumber ?? profile.phoneNumber} 
            onChange={(e) => handleChange('phoneNumber', e.target.value)} 
          />
          <TextInput 
            variant="filled" size="md"
            label="Address" 
            disabled={!editMode} 
            value={editedProfile.address ?? profile.address} 
            onChange={(e) => handleChange('address', e.target.value)} 
          />

          <Group justify='flex-end' mt="md">
            {!editMode ? (
              <Button onClick={() => setEditMode(true)}>Edit Profile</Button>
            ) : (
              <>
                <Button color="gray" onClick={handleCancel}>Cancel</Button>
                <Button loading={saving} onClick={handleSave}>Save Changes</Button>
              </>
            )}
          </Group>
        </>
      )}
    </Container>
  );
};

export default Profile;
