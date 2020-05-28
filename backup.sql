--
-- PostgreSQL database dump
--

-- Dumped from database version 12.2
-- Dumped by pg_dump version 12.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auth_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auth_group_id_seq OWNED BY public.auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auth_group_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auth_group_permissions_id_seq OWNED BY public.auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auth_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auth_permission_id_seq OWNED BY public.auth_permission.id;


--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


--
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auth_user_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auth_user_groups_id_seq OWNED BY public.auth_user_groups.id;


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auth_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auth_user_id_seq OWNED BY public.auth_user.id;


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.auth_user_user_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.auth_user_user_permissions_id_seq OWNED BY public.auth_user_user_permissions.id;


--
-- Name: dashboard_equityrates; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboard_equityrates (
    id integer NOT NULL,
    "sweatEquity" integer,
    "standTime" integer,
    "volunteerTime" integer
);


--
-- Name: dashboard_equityrates_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dashboard_equityrates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dashboard_equityrates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.dashboard_equityrates_id_seq OWNED BY public.dashboard_equityrates.id;


--
-- Name: dashboard_newsystemuser; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboard_newsystemuser (
    id integer NOT NULL,
    username character varying(40) NOT NULL,
    role character varying(20) NOT NULL,
    email character varying(254) NOT NULL,
    password character varying(32) NOT NULL
);


--
-- Name: dashboard_newsystemuser_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dashboard_newsystemuser_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dashboard_newsystemuser_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.dashboard_newsystemuser_id_seq OWNED BY public.dashboard_newsystemuser.id;


--
-- Name: dashboard_timelogs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboard_timelogs (
    id integer NOT NULL,
    person character varying(20) NOT NULL,
    activity character varying(20) NOT NULL,
    "startTime" character varying(40),
    "endTime" character varying(40),
    users_id integer NOT NULL
);


--
-- Name: dashboard_timelogs_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dashboard_timelogs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dashboard_timelogs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.dashboard_timelogs_id_seq OWNED BY public.dashboard_timelogs.id;


--
-- Name: dashboard_transactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboard_transactions (
    id integer NOT NULL,
    person character varying(20) NOT NULL,
    "transactionType" character varying(40) NOT NULL,
    amount integer,
    "paymentType" character varying(20),
    "paymentStatus" character varying(20),
    date character varying(40),
    users_id integer NOT NULL
);


--
-- Name: dashboard_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dashboard_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dashboard_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.dashboard_transactions_id_seq OWNED BY public.dashboard_transactions.id;


--
-- Name: dashboard_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.dashboard_users (
    id integer NOT NULL,
    firstname character varying(20) NOT NULL,
    middlename character varying(20) NOT NULL,
    lastname character varying(20) NOT NULL,
    "waiverAcceptedDate" character varying(40),
    "membershipExp" character varying(40),
    birthdate character varying(40),
    email character varying(40) NOT NULL,
    phone character varying(40) NOT NULL,
    "emergencyName" character varying(20) NOT NULL,
    relation character varying(20) NOT NULL,
    "emergencyPhone" character varying(40) NOT NULL,
    "lastVisit" character varying(40) NOT NULL,
    equity integer NOT NULL,
    waiver character varying(20) NOT NULL,
    permissions character varying(20) NOT NULL
);


--
-- Name: dashboard_users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.dashboard_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: dashboard_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.dashboard_users_id_seq OWNED BY public.dashboard_users.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.django_admin_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.django_admin_log_id_seq OWNED BY public.django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.django_content_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.django_content_type_id_seq OWNED BY public.django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_migrations (
    id integer NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.django_migrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


--
-- Name: auth_group id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group ALTER COLUMN id SET DEFAULT nextval('public.auth_group_id_seq'::regclass);


--
-- Name: auth_group_permissions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_group_permissions_id_seq'::regclass);


--
-- Name: auth_permission id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission ALTER COLUMN id SET DEFAULT nextval('public.auth_permission_id_seq'::regclass);


--
-- Name: auth_user id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_user ALTER COLUMN id SET DEFAULT nextval('public.auth_user_id_seq'::regclass);


--
-- Name: auth_user_groups id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_user_groups ALTER COLUMN id SET DEFAULT nextval('public.auth_user_groups_id_seq'::regclass);


--
-- Name: auth_user_user_permissions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_user_user_permissions_id_seq'::regclass);


--
-- Name: dashboard_equityrates id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_equityrates ALTER COLUMN id SET DEFAULT nextval('public.dashboard_equityrates_id_seq'::regclass);


--
-- Name: dashboard_newsystemuser id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_newsystemuser ALTER COLUMN id SET DEFAULT nextval('public.dashboard_newsystemuser_id_seq'::regclass);


--
-- Name: dashboard_timelogs id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_timelogs ALTER COLUMN id SET DEFAULT nextval('public.dashboard_timelogs_id_seq'::regclass);


--
-- Name: dashboard_transactions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_transactions ALTER COLUMN id SET DEFAULT nextval('public.dashboard_transactions_id_seq'::regclass);


--
-- Name: dashboard_users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_users ALTER COLUMN id SET DEFAULT nextval('public.dashboard_users_id_seq'::regclass);


--
-- Name: django_admin_log id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log ALTER COLUMN id SET DEFAULT nextval('public.django_admin_log_id_seq'::regclass);


--
-- Name: django_content_type id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type ALTER COLUMN id SET DEFAULT nextval('public.django_content_type_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add user	4	add_user
14	Can change user	4	change_user
15	Can delete user	4	delete_user
16	Can view user	4	view_user
17	Can add content type	5	add_contenttype
18	Can change content type	5	change_contenttype
19	Can delete content type	5	delete_contenttype
20	Can view content type	5	view_contenttype
21	Can add session	6	add_session
22	Can change session	6	change_session
23	Can delete session	6	delete_session
24	Can view session	6	view_session
25	Can add users	7	add_users
26	Can change users	7	change_users
27	Can delete users	7	delete_users
28	Can view users	7	view_users
29	Can add timelogs	8	add_timelogs
30	Can change timelogs	8	change_timelogs
31	Can delete timelogs	8	delete_timelogs
32	Can view timelogs	8	view_timelogs
33	Can add transactions	9	add_transactions
34	Can change transactions	9	change_transactions
35	Can delete transactions	9	delete_transactions
36	Can view transactions	9	view_transactions
37	Can add new system user	10	add_newsystemuser
38	Can change new system user	10	change_newsystemuser
39	Can delete new system user	10	delete_newsystemuser
40	Can view new system user	10	view_newsystemuser
41	Can add equity rates	11	add_equityrates
42	Can change equity rates	11	change_equityrates
43	Can delete equity rates	11	delete_equityrates
44	Can view equity rates	11	view_equityrates
\.


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
2	pbkdf2_sha256$180000$5LdHTatjQyHy$h47h7NTS6QEfLE6yL1omHk+Kb+xvKnCiD5YN6Oupdeg=	2020-05-28 16:23:41.467788-04	t	willcshapiro			willcshapiro@gmail.com	t	t	2020-04-23 11:06:31.328482-04
11	pbkdf2_sha256$180000$lp8v1jOfXNCE$dHzwEaCcQSUjFFGgHi0aHPoXjCGX+s35vW0ZeFQ4F9s=	2020-05-28 18:23:58.036789-04	f	appadmin	App Admin		willcshapiro@gmail.com	f	t	2020-05-28 16:46:04.26432-04
3	pbkdf2_sha256$180000$A2hhANPOUARy$O0FJKAzz9tojv6t1XxpVzoaFgnLMddcOlXsBdPCMvPI=	2020-05-13 21:12:39.098717-04	t	shop	shop		shop@thebrokespoke.org	t	t	2020-05-13 20:22:53-04
1	pbkdf2_sha256$180000$m02qSDuzI1U9$2alGo5vGGKIHTlDw1dZuSLDE7EAy2vP+amIXLSuPnVU=	2020-04-23 13:48:28-04	t	admin	shop-admin		willcshapiro@gmail.com	t	t	2020-04-09 21:08:44-04
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: dashboard_equityrates; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dashboard_equityrates (id, "sweatEquity", "standTime", "volunteerTime") FROM stdin;
\.


--
-- Data for Name: dashboard_newsystemuser; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dashboard_newsystemuser (id, username, role, email, password) FROM stdin;
1	willcshapiro	Shop Admin	willcshapiro@gmail.com	Packrat1@
2	shop@thebrokespoke.org	Shop Admin	shop@thebrokespoke.org	br0kesp0ke
\.


--
-- Data for Name: dashboard_timelogs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dashboard_timelogs (id, person, activity, "startTime", "endTime", users_id) FROM stdin;
119	Will Shapiro	volunteering	28/05/2020 20:28	28/05/2020 08:29 PM	1
120	sfsdf	volunteering	28/05/2020 20:28	28/05/2020 08:32 PM	1
121	Shapiro, Will	volunteering	28/05/2020 08:40	28/05/2020 09:20 PM	1
122	Shapiro, Will	volunteering	28/05/2020 09:27 PM	\N	1
\.


--
-- Data for Name: dashboard_transactions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dashboard_transactions (id, person, "transactionType", amount, "paymentType", "paymentStatus", date, users_id) FROM stdin;
8	Will Shapiro	Equity Bike Purchase	3	Cash/Credit	Complete	2020-05-13 18:54:01.	1
10	k		0	0	0	2020-05-25 19:23:10.	1
11	Will asdasd		0	0	0	2020-05-25 19:23:42.	1
12	test	Equity Parts Purchase	4	Cash/Credit	Complete	2020-05-25 19:26:14.	1
13	ksdf	Equity Bike Purchase	32	0	0	2020-05-25 19:29:48.	1
\.


--
-- Data for Name: dashboard_users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.dashboard_users (id, firstname, middlename, lastname, "waiverAcceptedDate", "membershipExp", birthdate, email, phone, "emergencyName", relation, "emergencyPhone", "lastVisit", equity, waiver, permissions) FROM stdin;
2	billy	b	bob	2020-05-25 15:00:00+	2020-05-25 19:00:00+	2020-05-25 00:00:00+	willcshapiro@gmail.com	34790	123123	frendo	2343	NULL	0	NULL	NULL
3	bon	bing	shlater	2020-05-28 14:14:00+00:00	2020-05-28 14:14:00+00:00	2020-05-28 14:14:00+00:00	willcshapiro@gmail.com	3479079209	sclabert	uncle	3479079209	NULL	0	NULL	NULL
1	Will	A	Shapiro	1998-12-25 00:00:00+	1998-12-25 00:00:00+	1998-12-25 00:00:00+	willcshapiro@gmail.com	34790	123123	dad	347909	1998-12-25 00:00:00+	4	NULL	NULL
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2020-05-13 20:22:53.703267-04	3	shop@thebrokespoke.org	1	[{"added": {}}]	4	2
2	2020-05-13 20:23:21.98967-04	3	shop@thebrokespoke.org	2	[{"changed": {"fields": ["Staff status", "Superuser status"]}}]	4	2
3	2020-05-13 20:23:27.873336-04	3	shop@thebrokespoke.org	2	[]	4	2
4	2020-05-13 20:23:51.323414-04	3	shop@thebrokespoke.org	2	[{"changed": {"fields": ["Email address"]}}]	4	2
5	2020-05-13 20:24:51.762671-04	3	shop	2	[{"changed": {"fields": ["Username", "First name"]}}]	4	3
6	2020-05-14 12:44:58.121741-04	1	admin	2	[{"changed": {"fields": ["First name"]}}]	4	3
7	2020-05-14 13:35:25.126107-04	5	shop2	3		4	2
8	2020-05-14 13:35:25.127747-04	6	shop22	3		4	2
9	2020-05-14 13:35:25.128731-04	7	ssdfsdf	3		4	2
10	2020-05-14 13:35:25.13066-04	8	wewfwefwe	3		4	2
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	auth	user
5	contenttypes	contenttype
6	sessions	session
7	dashboard	users
8	dashboard	timelogs
9	dashboard	transactions
10	dashboard	newsystemuser
11	dashboard	equityrates
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
39	contenttypes	0001_initial	2020-05-11 20:03:12.020687-04
40	auth	0001_initial	2020-05-11 20:03:12.031546-04
41	admin	0001_initial	2020-05-11 20:03:12.038117-04
42	admin	0002_logentry_remove_auto_add	2020-05-11 20:03:12.046705-04
43	admin	0003_logentry_add_action_flag_choices	2020-05-11 20:03:12.055509-04
44	contenttypes	0002_remove_content_type_name	2020-05-11 20:05:26.436746-04
45	dashboard	0001_initial	2020-05-11 20:07:21.370832-04
46	auth	0002_alter_permission_name_max_length	2020-05-11 20:08:12.177843-04
47	auth	0003_alter_user_email_max_length	2020-05-11 20:08:12.189726-04
48	auth	0004_alter_user_username_opts	2020-05-11 20:08:12.198519-04
49	auth	0005_alter_user_last_login_null	2020-05-11 20:08:12.210063-04
50	auth	0006_require_contenttypes_0002	2020-05-11 20:08:12.211654-04
51	auth	0007_alter_validators_add_error_messages	2020-05-11 20:08:12.219495-04
52	auth	0008_alter_user_username_max_length	2020-05-11 20:08:12.231073-04
53	auth	0009_alter_user_last_name_max_length	2020-05-11 20:08:12.240289-04
54	auth	0010_alter_group_name_max_length	2020-05-11 20:08:12.247699-04
55	auth	0011_update_proxy_permissions	2020-05-11 20:08:12.258199-04
56	sessions	0001_initial	2020-05-12 15:59:09.534822-04
57	dashboard	0002_auto_20200512_1959	2020-05-12 15:59:19.693279-04
58	dashboard	0003_auto_20200512_2010	2020-05-12 16:10:30.464056-04
59	dashboard	0002_auto_20200513_1641	2020-05-13 12:41:50.305787-04
60	dashboard	0003_newsystemuser	2020-05-13 13:37:01.604068-04
61	dashboard	0004_auto_20200513_1853	2020-05-13 14:53:40.448114-04
62	dashboard	0005_auto_20200514_0002	2020-05-13 20:02:04.584999-04
63	dashboard	0006_auto_20200525_2104	2020-05-25 17:04:12.451492-04
64	dashboard	0007_auto_20200525_2153	2020-05-25 17:53:24.785055-04
65	dashboard	0008_equityrates	2020-05-25 22:26:15.332007-04
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
9em4sbaasptazccefnorgdpnrntzkuf4	YWIwNDczYzgyNjBhMDM2YzMyYWYyOTZhY2E5YWY2ZDNhMWVmOWRmMzp7Il9hdXRoX3VzZXJfaWQiOiIyIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI0MDE3YjhhMDk3Y2IxNWVlYmJhZDg4Yzc1OGExMTZiYmEyZDExZjg4In0=	2020-05-28 14:33:56.407805-04
fzcg1ji095l3xcrifbt7qki3syj7uxop	YWIwNDczYzgyNjBhMDM2YzMyYWYyOTZhY2E5YWY2ZDNhMWVmOWRmMzp7Il9hdXRoX3VzZXJfaWQiOiIyIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiI0MDE3YjhhMDk3Y2IxNWVlYmJhZDg4Yzc1OGExMTZiYmEyZDExZjg4In0=	2020-06-05 23:07:47.485401-04
9hok6rnacs0mdszrzxxe3c132iffqg6d	ZDcyMmM1MWFiYzRlZDE0NzEzMTNmMjE1ZWQ4YjYwZWI4MTEwMjRiYjp7Il9hdXRoX3VzZXJfaWQiOiIxMSIsIl9hdXRoX3VzZXJfYmFja2VuZCI6ImRqYW5nby5jb250cmliLmF1dGguYmFja2VuZHMuTW9kZWxCYWNrZW5kIiwiX2F1dGhfdXNlcl9oYXNoIjoiZWMzMTM3MDhlYmYwNGEwYTlhNTg0YTczNmZjNzI0YjdkYzUxOTIyZCJ9	2020-06-11 18:23:58.081787-04
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 44, true);


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_user_groups_id_seq', 1, false);


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_user_id_seq', 11, true);


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_user_user_permissions_id_seq', 1, false);


--
-- Name: dashboard_equityrates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dashboard_equityrates_id_seq', 1, false);


--
-- Name: dashboard_newsystemuser_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dashboard_newsystemuser_id_seq', 2, true);


--
-- Name: dashboard_timelogs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dashboard_timelogs_id_seq', 123, true);


--
-- Name: dashboard_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dashboard_transactions_id_seq', 13, true);


--
-- Name: dashboard_users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.dashboard_users_id_seq', 3, true);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 10, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 11, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 65, true);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_user_id_group_id_94350c0c_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id);


--
-- Name: auth_user auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_permission_id_14a6b632_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id);


--
-- Name: auth_user auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: dashboard_equityrates dashboard_equityrates_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_equityrates
    ADD CONSTRAINT dashboard_equityrates_pkey PRIMARY KEY (id);


--
-- Name: dashboard_newsystemuser dashboard_newsystemuser_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_newsystemuser
    ADD CONSTRAINT dashboard_newsystemuser_pkey PRIMARY KEY (id);


--
-- Name: dashboard_timelogs dashboard_timelogs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_timelogs
    ADD CONSTRAINT dashboard_timelogs_pkey PRIMARY KEY (id);


--
-- Name: dashboard_transactions dashboard_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_transactions
    ADD CONSTRAINT dashboard_transactions_pkey PRIMARY KEY (id);


--
-- Name: dashboard_users dashboard_users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_users
    ADD CONSTRAINT dashboard_users_pkey PRIMARY KEY (id);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: auth_user_groups_group_id_97559544; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_user_groups_group_id_97559544 ON public.auth_user_groups USING btree (group_id);


--
-- Name: auth_user_groups_user_id_6a12ed8b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_user_groups_user_id_6a12ed8b ON public.auth_user_groups USING btree (user_id);


--
-- Name: auth_user_user_permissions_permission_id_1fbb5f2c; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON public.auth_user_user_permissions USING btree (permission_id);


--
-- Name: auth_user_user_permissions_user_id_a95ead1b; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON public.auth_user_user_permissions USING btree (user_id);


--
-- Name: auth_user_username_6821ab7c_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_user_username_6821ab7c_like ON public.auth_user USING btree (username varchar_pattern_ops);


--
-- Name: dashboard_timelogs_users_id_cdb95836; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dashboard_timelogs_users_id_cdb95836 ON public.dashboard_timelogs USING btree (users_id);


--
-- Name: dashboard_transactions_users_id_f21c2f6d; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX dashboard_transactions_users_id_f21c2f6d ON public.dashboard_transactions USING btree (users_id);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_group_id_97559544_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_user_id_6a12ed8b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dashboard_timelogs dashboard_timelogs_users_id_cdb95836_fk_dashboard_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_timelogs
    ADD CONSTRAINT dashboard_timelogs_users_id_cdb95836_fk_dashboard_users_id FOREIGN KEY (users_id) REFERENCES public.dashboard_users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: dashboard_transactions dashboard_transactions_users_id_f21c2f6d_fk_dashboard_users_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.dashboard_transactions
    ADD CONSTRAINT dashboard_transactions_users_id_f21c2f6d_fk_dashboard_users_id FOREIGN KEY (users_id) REFERENCES public.dashboard_users(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

