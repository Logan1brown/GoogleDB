-- Create role management tables
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    role TEXT NOT NULL CHECK (role IN ('admin', 'editor', 'viewer')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by UUID REFERENCES auth.users(id)
);

CREATE TABLE IF NOT EXISTS role_changes (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id),
    old_role TEXT CHECK (old_role IN ('admin', 'editor', 'viewer')),
    new_role TEXT CHECK (new_role IN ('admin', 'editor', 'viewer')),
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    changed_by UUID REFERENCES auth.users(id),
    reason TEXT
);

-- Create RLS policies
ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_changes ENABLE ROW LEVEL SECURITY;

-- Viewers can read their own role
CREATE POLICY "users_can_read_own_role" 
    ON user_roles FOR SELECT 
    USING (auth.uid() = id);

-- Admins can do everything
CREATE POLICY "admins_can_manage_roles" 
    ON user_roles FOR ALL 
    USING (auth.role() = 'admin')
    WITH CHECK (auth.role() = 'admin');

CREATE POLICY "admins_can_view_role_changes" 
    ON role_changes FOR SELECT 
    USING (auth.role() = 'admin');

-- Create trigger for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_roles_updated_at
    BEFORE UPDATE ON user_roles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

-- Create first admin user if not exists

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM user_roles WHERE role = 'admin') THEN
        INSERT INTO user_roles (id, role)
        SELECT id, 'admin'
        FROM auth.users
        WHERE email = 'logan1brown@gmail.com'
        LIMIT 1;
        
        RAISE NOTICE 'Created admin role for logan1brown@gmail.com';
    END IF;
END
$$;
