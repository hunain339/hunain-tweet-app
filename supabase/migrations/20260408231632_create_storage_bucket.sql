-- Create public storage bucket for tweet photos
insert into storage.buckets (id, name, public)
values ('tweet-photos', 'tweet-photos', true)
on conflict (id) do nothing;

-- Allow public access to read photos
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'objects' 
        AND schemaname = 'storage' 
        AND policyname = 'Public Access to Tweet Photos'
    ) THEN
        CREATE POLICY "Public Access to Tweet Photos" ON storage.objects
        FOR SELECT TO public
        USING (bucket_id = 'tweet-photos');
    END IF;
END
$$;

-- Allow authenticated users to upload photos
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'objects' 
        AND schemaname = 'storage' 
        AND policyname = 'Authenticated Upload Access'
    ) THEN
        CREATE POLICY "Authenticated Upload Access" ON storage.objects
        FOR INSERT TO authenticated
        WITH CHECK (bucket_id = 'tweet-photos');
    END IF;
END
$$;
