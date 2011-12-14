<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<!--
	Name: Basic Tumbler.com API Utility
	Version: 1.1
	Author: Josh Nichols <mrblank@gmail.com>
	URL: http://www.joshnichols.com/
	
	Description:
	This utility transforms a basic Tumblr.com XML source into XHTML. Each post is grouped by date and is marked up in a way that allows for easy styling with CSS.	
	Data source:
	Requires a Dynamic XML data source using Tumblr.com's API named "get-tumblr". API documentation: http://www.tumblr.com/api
	Example: http://mrblank.tumblr.com/api/read/
	
	To do:
	Include some starter CSS rules.	
-->
    
    <xsl:key name="post-date" match="post" use="substring(@date, 6, 11)"/>
    
    <!-- The template matches on the name of your Tumblr data source -->
    <xsl:template match="get-tumblr">
	    
        <xsl:param name="tumblr-url" select="tumblr/tumblelog/@cname"/>
        <xsl:param name="tumblr-name" select="tumblr/tumblelog/@title"/>
        <xsl:param name="tumblr-description" select="tumblr/tumblelog"/>

        <div id="tumblelog"> 
            <h2><xsl:value-of select="$tumblr-name"/></h2>
            <p><xsl:value-of select="$tumblr-description"/></p>
            <xsl:choose>
                <xsl:when test="error">
                    <div class="entries">
                        <p>The Tumblr.com feed is down right now, sorry. <a href="http://{$tumblr-url}">Try visiting my Tumblelog there</a>, or check back later.</p>
                    </div>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:apply-templates select="tumblr/posts"/>
                </xsl:otherwise>
            </xsl:choose>
            <p>
                <a href="http://{$tumblr-url}/archive">Browse the tumblelog archive &#8594;</a>
            </p>
        </div>
    </xsl:template>
    <!-- Groups posts by day using the Key value -->
    <xsl:template match="posts">
        <xsl:for-each  select="post[generate-id() = generate-id (key('post-date', substring(@date, 6, 11))[1])]">
            <div class="tumblr-entries">
                <div class="date">
                    <span class="year">
                        <xsl:value-of select="substring(@date, 13, 4)"/>
                    </span>
                    <span class="month">
                        <xsl:value-of select="substring(@date, 9, 3)"/>
                    </span>
                    <span class="day">
                        <xsl:choose>
                            <xsl:when test="substring(@date, 6, 1) = 0">
                                <xsl:value-of select="substring(@date, 7, 1)"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="substring(@date, 6, 2)"/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </span>
                </div>
                <!-- Post types -->
                <xsl:for-each select="key('post-date', substring(@date, 6, 11))">
                    <xsl:choose>
                        <!-- Regular type -->
                        <xsl:when test="@type='regular'">
                            <div class="tumblr-entry regular">
                                <xsl:apply-templates select="@url" mode="tumblr-meta">
                                    <xsl:with-param name="label" select="'Image'"/>
                                </xsl:apply-templates>
                                <xsl:if test="regular-title">
                                    <h3>
                                        <a href="{.}" title="Permalink to this post on Tumblr">
                                            <xsl:value-of select="regular-title"/>
                                        </a>
                                    </h3>
                                </xsl:if>
                                <div class="regular-body">
                                    <xsl:apply-templates select="regular-body" mode="tumblr-body"/>
                                </div>
                            </div>
                        </xsl:when>
                        <!-- Type photo -->
                        <xsl:when test="@type='photo'">
                            <div class="tumblr-entry photo">
                                <xsl:apply-templates select="@url" mode="tumblr-meta">
                                    <xsl:with-param name="label" select="'Image'"/>
                                </xsl:apply-templates>
                                <div class="photo-url">
                                    <!-- image "max-width" sizes are 75, 100, 250, 400 and 500 -->
                                    <img src="{photo-url[@max-width='500']}" alt="Tumblelog image"/>
                                </div>
                                <xsl:apply-templates select="photo-caption" mode="tumblr-body"/>
                            </div>
                        </xsl:when>
                        <!-- Link text -->
                        <xsl:when test="@type='link'">
                            <div class="tumblr-entry link">
                                <xsl:apply-templates select="@url" mode="tumblr-meta">
                                    <xsl:with-param name="label" select="'Link'"/>
                                </xsl:apply-templates>
                                <xsl:choose>
                                    <xsl:when test="link-text">
                                        <h3>
                                            <a href="{link-url}" title="Visit this link">
                                                <xsl:value-of select="link-text"/>
                                            </a>
                                        </h3>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <p>
                                            <a href="{link-url}" title="Visit this link">
                                                <xsl:value-of select="link-url"/>
                                            </a>
                                        </p>
                                    </xsl:otherwise>
                                </xsl:choose>
                                <xsl:apply-templates select="link-description" mode="tumblr-body"/>
                            </div>
                        </xsl:when>
                        <!-- Quote type -->
                        <xsl:when test="@type='quote'">
                            <div class="tumblr-entry quote">
                                <xsl:apply-templates select="@url" mode="tumblr-meta">
                                    <xsl:with-param name="label" select="'Quote'"/>
                                </xsl:apply-templates>
                                <blockquote>
                                    <xsl:value-of select="quote-text" disable-output-escaping="yes"/>
                                </blockquote>
                                <xsl:if test="quote-source">
                                    <div class="quote-source">
                                        <p>&#8212; <xsl:value-of select="quote-source" disable-output-escaping="yes"/></p>       
                                    </div>
                                </xsl:if>
                            </div>
                        </xsl:when>
                        <!-- Video type -->
                        <xsl:when test="@type='video'">
                            <div class="tumblr-entry video">
                                <xsl:apply-templates select="@url" mode="tumblr-meta">
                                    <xsl:with-param name="label" select="'Video'"/>
                                </xsl:apply-templates>
                                <div class="video-embed">
                                	<!-- Using "video-player" makes videos 400px wide, "video-source" uses the source dimentions. -->
                                    <xsl:value-of select="video-player" disable-output-escaping="yes"/>
                                </div>
                                <xsl:apply-templates select="video-caption" mode="tumblr-body"/>
                            </div>
                        </xsl:when>
                        <!-- Audio type -->
                        <xsl:when test="@type='audio'">
                            <div class="tumblr-entry audio">
                                <xsl:apply-templates select="@url" mode="tumblr-meta">
                                    <xsl:with-param name="label" select="'Audio'"/>
                                </xsl:apply-templates>
                                <div class="audio-player">
                                    <xsl:value-of select="substring-before(audio-player,'.swf')" disable-output-escaping="yes"/>
                                    <xsl:text>_black</xsl:text>
                                    <xsl:value-of select="substring-after(audio-player,'audio_player')" disable-output-escaping="yes"/>
                                </div>
                                <xsl:apply-templates select="audio-caption" mode="tumblr-body"/>
                            </div>
                        </xsl:when>
                        <!-- Chat type -->
                        <xsl:when test="@type='conversation'">
                            <div class="tumblr-entry conversation">
                                <xsl:apply-templates select="@url" mode="tumblr-meta">
                                    <xsl:with-param name="label" select="'Chat'"/>
                                </xsl:apply-templates>
                                <xsl:if test="conversation-title">
                                    <div class="conversation-title">
                                        <h3><xsl:value-of select="conversation-title"/></h3>       
                                    </div>
                                </xsl:if>
                                <ol>
                                    <xsl:for-each select="conversation/line">
                                        <li>
                                            <!-- This adds a class of "odd" to every other <li> so you can zebra stripe chats. -->
                                            <xsl:if test="(position() mod 2) = 1">
                                                <xsl:attribute name="class">odd</xsl:attribute>
                                            </xsl:if>
                                            <span><xsl:value-of select="@name"/></span>
                                            <xsl:text>: </xsl:text>
                                            <xsl:value-of select="." disable-output-escaping="yes"/>
                                        </li>
                                    </xsl:for-each>
                                </ol>
                            </div>
                        </xsl:when>
                        <!-- End types -->
                    </xsl:choose>
                    <!-- End post types -->
                </xsl:for-each>
            </div>
        </xsl:for-each>
    </xsl:template>
    
    <!-- Meta information for each post -->
    <xsl:template match="@url" mode="tumblr-meta">
        
        <xsl:param name="label"/>
       
        <div class="meta">
            <xsl:value-of select="$label"/>
            <xsl:text> // </xsl:text>
            <a href="{.}" title="Permalink to this post on Tumblr">Permalink &#8734;</a>
        </div>
    </xsl:template>
    
    <!-- Output from a text area -->
    <xsl:template match="*" mode="tumblr-body">
        <div class="{name(.)}">
            <!-- If there is only 1 paragraph in a text area, Tumbler doesn't output <p> tags. This makes consistent styling difficult. -->
            <!-- The <choose> statement below checks for <p>, <h1-6> and <blockquote> tags. If they don't exist, it adds the <p> tag. -->
            <!-- If you don't like this, remove the <choose> and replace it with this: <xsl:value-of select="regular-body" disable-output-escaping="yes"/> -->    
            <xsl:choose>
                <xsl:when test="substring(., 1, 2) = '&lt;p'">
                    <xsl:value-of select="." disable-output-escaping="yes"/>
                </xsl:when>
                <xsl:when test="substring(., 1, 2) = '&lt;h'">
                    <xsl:value-of select="." disable-output-escaping="yes"/>
                </xsl:when>
                <xsl:when test="substring(., 1, 2) = '&lt;b'">
                    <xsl:value-of select="." disable-output-escaping="yes"/>
                </xsl:when>
                <xsl:otherwise>
                    <p><xsl:value-of select="." disable-output-escaping="yes"/></p>
                </xsl:otherwise>
            </xsl:choose>
        </div>
    </xsl:template>
        
</xsl:stylesheet>